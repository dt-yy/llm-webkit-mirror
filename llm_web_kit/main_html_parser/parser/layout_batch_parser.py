import json
import re
from hashlib import sha256

import nltk
from lxml import html
from lxml.html import etree
from nltk.tokenize import word_tokenize

from llm_web_kit.html_layout.html_layout_cosin import get_feature, similarity
from llm_web_kit.input.pre_data_json import PreDataJson, PreDataJsonKey
from llm_web_kit.libs.html_utils import element_to_html, html_to_element
from llm_web_kit.main_html_parser.parser.parser import BaseMainHtmlParser

nltk.download('punkt', quiet=True)  # 静默模式避免日志干扰

MAX_LENGTH = 10
SIMILARITY_THRESHOLD = 0.75
DYNAMIC_ID_SIM_THRESHOLD = 0.9


class LayoutBatchParser(BaseMainHtmlParser):
    """完整处理流程."""

    def __init__(self, template_data: str | dict):
        # 确保模板数据的键是整数类型
        self.template_data = template_data
        self.dynamic_id_enable = False
        self.dynamic_classid_enable = False

    def parse_tuple_key(self, key_str):
        if key_str.startswith('(') and key_str.endswith(')'):
            try:
                return eval(key_str)  # WARNING: eval is unsafe for untrusted data!
            except (SyntaxError, ValueError):
                return key_str  # Fallback if parsing fails
        return key_str

    def parse(self, pre_data: PreDataJson) -> PreDataJson:
        # 支持输入字符串和tag mapping后的dict对象
        html_source = pre_data[PreDataJsonKey.HTML_SOURCE]
        template_dict_html = pre_data.get(PreDataJsonKey.TYPICAL_DICT_HTML, '<html></html>')
        self.dynamic_id_enable = pre_data.get(PreDataJsonKey.DYNAMIC_ID_ENABLE, False)
        self.dynamic_classid_enable = pre_data.get('dynamic_classid_enable', False)
        template_data_str = pre_data[PreDataJsonKey.HTML_ELEMENT_DICT]
        template_data = dict()
        if isinstance(template_data_str, str):
            template_data_str = json.loads(template_data_str)
            for layer, layer_dict in template_data_str.items():
                layer_dict_json = {self.parse_tuple_key(k): v for k, v in layer_dict.items()}
                template_data[int(layer)] = layer_dict_json
        elif isinstance(template_data_str, dict):
            template_data = template_data_str
        else:
            raise ValueError(f'template_data 类型错误: {type(template_data_str)}')
        self.template_data = template_data
        content, body = self.process(html_source, template_dict_html)

        # 相似度计算
        if pre_data.get(PreDataJsonKey.TYPICAL_MAIN_HTML, None):
            template_main_html = pre_data[PreDataJsonKey.TYPICAL_MAIN_HTML]
            if pre_data.get(PreDataJsonKey.SIMILARITY_LAYER, None):
                layer = pre_data[PreDataJsonKey.SIMILARITY_LAYER]
            else:
                layer = self.__get_max_width_layer(template_data)
            feature1 = get_feature(template_main_html)
            feature2 = get_feature(body)
            sim = None
            if feature1 is not None and feature2 is not None:
                sim = similarity(feature1, feature2, layer_n=layer)
            if sim is None or sim < SIMILARITY_THRESHOLD:
                pre_data[PreDataJsonKey.MAIN_HTML_SUCCESS] = False
            else:
                pre_data[PreDataJsonKey.MAIN_HTML_SUCCESS] = True

        # 结果返回
        pre_data[PreDataJsonKey.MAIN_HTML] = content
        pre_data[PreDataJsonKey.MAIN_HTML_BODY] = body
        return pre_data

    def get_element_id(self, element):
        """生成稳定的短哈希ID."""
        element_html = html.tostring(element, encoding='unicode', method='html')
        return f'id{sha256(element_html.encode()).hexdigest()}'  # 10位哈希

    def process(self, html_source: str, template_dict_html: str) -> str:
        # 根据颜色删减html_source
        processed_html = self.drop_node_element(html_source, self.template_data, template_dict_html)
        content, body = self.htmll_to_content2(processed_html)
        return content, body

    def get_tokens(self, content):
        tokens = word_tokenize(content)
        return tokens

    def normalize_key(self, tup):
        if not tup:
            return None
        tag, class_id, idd = tup
        # 如果有id，则无需判断class，因为有的网页和模版id相同，但是class不同
        if tag in ['body', 'html']:
            return (tag, None, None)
        if idd:
            return (tag, None, self.replace_post_number(idd))
        return (tag, self.replace_post_number(class_id), self.replace_post_number(idd))

    def replace_post_number(self, text):
        if not text:
            return None
        # 匹配 "post-数字" 或 "postid-数字"（不区分大小写），并替换数字部分为空
        pattern = r'(post|postid)-(\d+)'
        # 使用 \1 保留前面的 "post" 或 "postid"，但替换数字部分
        return re.sub(pattern, lambda m: f'{m.group(1)}-', text, flags=re.IGNORECASE)

    def find_blocks_drop(self, element, depth, element_dict, parent_keyy, parent_label, template_doc):
        # 判断这个tag是否有id
        if isinstance(element, etree._Comment):
            return
        length = len(self.get_tokens(element.text_content().strip()))
        length_tail = 0
        if element.tail:
            length_tail = len(element.tail.strip())
        idd = element.get('id')
        tag = element.tag
        layer_nodes = element_dict[depth]
        class_tag = element.get('class')
        ori_keyy = (tag, class_tag, idd)
        keyy = self.normalize_key(ori_keyy)

        # 获取element的当前层的所有节点
        element_parent = element.getparent()
        current_layer_keys = {}
        if element_parent is None:
            child_str = html.tostring(element, encoding='utf-8').decode()
            current_layer_keys[keyy] = (ori_keyy, child_str)
        else:
            for child in element_parent:
                if isinstance(child, etree._Comment):
                    continue
                child_ori_key = (child.tag, child.get('class'), child.get('id'))
                child_key = self.normalize_key(child_ori_key)
                child_str = html.tostring(child, encoding='utf-8').decode()
                current_layer_keys[child_key] = (child_ori_key, child_str)

        # 匹配正文节点
        has_red = False
        layer_nodes_dict = dict()
        layer_norm_eles = {}
        # 构造当前层的候选映射字典
        for ele_keyy, ele_value in layer_nodes.items():
            ele_parent_keyy = self.normalize_key(ele_value[1])
            if ele_parent_keyy is not None:
                ele_parent_keyy = tuple(ele_parent_keyy)
            ele_label = ele_value[0]
            norm_ele_keyy = self.normalize_key(ele_keyy[:3])
            if norm_ele_keyy in layer_norm_eles:
                layer_norm_eles[norm_ele_keyy].append((ele_label, ele_keyy[:3], ele_parent_keyy))
            else:
                layer_norm_eles[norm_ele_keyy] = [(ele_label, ele_keyy[:3], ele_parent_keyy)]
        # 尝试匹配当前层每个节点，判断是否存在至少一个红色节点
        for current_layer_key, current_layer_value in current_layer_keys.items():
            current_layer_ori_key = current_layer_value[0]
            node_html = current_layer_value[1]
            if current_layer_key in layer_norm_eles:
                for layer_norm_ele_value in layer_norm_eles[current_layer_key]:
                    if layer_norm_ele_value[2] != parent_keyy:
                        continue
                    node_label = layer_norm_ele_value[0]

                    if current_layer_key in layer_nodes_dict:
                        layer_nodes_dict[current_layer_key].append(node_label)
                    else:
                        layer_nodes_dict[current_layer_key] = [node_label]
                    if node_label == 'red':
                        has_red = True
                        break
            # 动态id匹配逻辑
            elif self.dynamic_id_enable and current_layer_key[2]:
                node_label, matched_ele_key = self.__match_tag_class(layer_nodes, current_layer_ori_key, parent_keyy,
                                                                     node_html, template_doc)
                if node_label is None and self.dynamic_classid_enable:
                    node_label, matched_ele_key = self.__match_tag(layer_nodes, current_layer_ori_key, parent_keyy,
                                                                   node_html,
                                                                   template_doc, False, True)
                if node_label is None:
                    continue
                # 采用element dict中的key来替换
                if current_layer_key == keyy:
                    keyy = matched_ele_key
                    element.set('id', matched_ele_key[2])
                if current_layer_key in layer_nodes_dict:
                    layer_nodes_dict[matched_ele_key].append(node_label)
                else:
                    layer_nodes_dict[matched_ele_key] = [node_label]

                if node_label == 'red':
                    has_red = True
            elif self.dynamic_id_enable and self.dynamic_classid_enable and current_layer_key[1]:
                node_label, matched_ele_key = self.__match_tag(layer_nodes, current_layer_ori_key, parent_keyy,
                                                               node_html,
                                                               template_doc, True, False)
                if node_label is None:
                    continue
                # 采用element dict中的key来替换
                if current_layer_key == keyy:
                    keyy = matched_ele_key
                    element.set('class', matched_ele_key[1])
                if current_layer_key in layer_nodes_dict:
                    layer_nodes_dict[matched_ele_key].append(node_label)
                else:
                    layer_nodes_dict[matched_ele_key] = [node_label]
                if node_label == 'red':
                    has_red = True

        if not has_red and parent_label != 'red':
            parent = element.getparent()
            if parent is not None:
                parent.remove(element)
            return
        # 当前层无红色节点，但父节点是红的，则整体输出这一层
        elif not has_red and parent_label == 'red':
            return
        label = None
        # 判断当前节点是否是红色节点
        if keyy in layer_nodes_dict:
            if 'red' not in layer_nodes_dict[keyy]:
                parent = element.getparent()
                if parent is not None:
                    parent.remove(element)
                return
            else:
                label = 'red'
        elif length > 0 or length_tail > 0:
            return

        for child in element:
            self.find_blocks_drop(child, depth + 1, element_dict, keyy, label, template_doc)

    def drop_node_element(self, html_source, element_dict, template_dict_html):
        # 解析 HTML 内容
        tree = html_to_element(html_source)
        doc = html_to_element(template_dict_html)
        self.find_blocks_drop(tree, 0, element_dict, None, '', doc)
        return element_to_html(tree)

    def htmll_to_content2(self, body_str):
        body = html.fromstring(body_str)
        tags_to_remove = ['header', 'footer', 'nav', 'aside', 'script', 'style']
        for tag in tags_to_remove:
            for element in body.xpath(f'//{tag}'):
                element.getparent().remove(element)
        self.add_newline_after_tags(body, ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'span', 'div', 'p', 'li'])
        output = []
        main_content = re.split(r'\n{1,}', self.get_text_with_newlines(body))
        for line in main_content:
            if line.strip():
                output.append(line)
        return '\n\n'.join(output), element_to_html(body)

    def add_newline_after_tags(self, element, tags):
        # Find all specified tags
        for tag in tags:
            for elem in element.xpath(f'//{tag}'):
                # Add a newline character after each specified tag
                if elem.tail:
                    elem.tail = '\n' + elem.tail
                else:
                    elem.tail = '\n'

    def get_text_with_newlines(self, element):
        text = []
        for item in element.iter():
            if item.tag in ['br', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr', 'div']:
                text.append(item.text if item.text else '')
                text.append('\n')
            elif item.tag in ['td', 'th']:
                text.append(item.text if item.text else '')
                text.append('\t')
            else:
                text.append(item.text if item.text else '')

            if item.tail:
                text.append(item.tail)

        return ''.join(text)

    def __get_max_width_layer(self, element_dict):
        max_length = 0
        max_width_layer = 0
        for layer_n, layer in element_dict.items():
            if len(layer) > max_length:
                max_width_layer = layer_n
                max_length = len(layer)

        return max_width_layer - 2 if max_width_layer > 4 else 3

    def __match_tag_class(self, layer_nodes, current_layer_key, parent_key, node_html, template_doc):
        # 构建主键和父键的key
        current_norm_key = (self.normalize_key((current_layer_key[0], current_layer_key[1], None)), parent_key)
        # 构建tag class字典
        for ele_keyy, ele_value in layer_nodes.items():
            # id要存在
            if not ele_keyy[2]:
                continue
            xpath = ele_value[2]
            ele_parent_keyy = self.normalize_key(ele_value[1])
            if ele_parent_keyy is not None:
                ele_parent_keyy = tuple(ele_parent_keyy)
            ele_label = ele_value[0]
            norm_ele_keyy = self.normalize_key((ele_keyy[0], ele_keyy[1], None))
            norm_ele_keyy_parent = (norm_ele_keyy, ele_parent_keyy)
            if current_norm_key == norm_ele_keyy_parent:
                # 计算3层相似度
                ele_root = template_doc.xpath(xpath)[0]
                ele_html = html.tostring(ele_root, encoding='utf-8').decode()
                feature1 = get_feature(ele_html)
                feature2 = get_feature(node_html)
                if feature1 is None or feature2 is None:
                    # logger.info(ele_keyy, ' getting feature failed')
                    continue
                template_sim = similarity(feature1, feature2, layer_n=3)

                if template_sim > DYNAMIC_ID_SIM_THRESHOLD:
                    return ele_label, self.normalize_key(ele_keyy[0:3])
                # else:
                # logger.info(f'{current_layer_key} and {ele_keyy} similarity is {template_sim}')
        return None, None

    def __match_tag(self, layer_nodes, current_layer_key, parent_key, node_html, template_doc, class_must=False,
                    id_exist=False):
        current_norm_key = (self.normalize_key((current_layer_key[0], None, None)), parent_key)
        for ele_keyy, ele_value in layer_nodes.items():
            # class id要存在
            if class_must and not ele_keyy[1]:
                continue
            if (id_exist and not ele_keyy[2]) or (not id_exist and ele_keyy[2]):
                continue

            xpath = ele_value[2]
            ele_parent_keyy = self.normalize_key(ele_value[1])
            if ele_parent_keyy is not None:
                ele_parent_keyy = tuple(ele_parent_keyy)
            ele_label = ele_value[0]
            norm_ele_keyy = self.normalize_key((ele_keyy[0], None, None))
            norm_ele_keyy_parent = (norm_ele_keyy, ele_parent_keyy)
            if current_norm_key == norm_ele_keyy_parent:
                # 计算3层相似度
                ele_root = template_doc.xpath(xpath)[0]
                ele_html = html.tostring(ele_root, encoding='utf-8').decode()
                feature1 = get_feature(ele_html)
                feature2 = get_feature(node_html)
                if feature1 is None or feature2 is None:
                    continue
                template_sim = similarity(feature1, feature2, layer_n=3)
                if template_sim > 0.9:
                    return ele_label, self.normalize_key(ele_keyy[0:3])
        return None, None
