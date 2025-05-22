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
from llm_web_kit.main_html_parser.parser.libs.tag_mapping import \
    MapItemToHtmlTagsParser
from llm_web_kit.main_html_parser.parser.parser import BaseMainHtmlParser

nltk.download('punkt', quiet=True)  # 静默模式避免日志干扰

MAX_LENGTH = 10
SIMILARITY_THRESHOLD = 0.75


class LayoutBatchParser(BaseMainHtmlParser):
    """完整处理流程."""
    def __init__(self, data_dict: dict):
        self.template_data = self.format_element_dict(data_dict['html_element_dict'])
        self.test_element_dict = self.get_tag_mapping(data_dict['html_source'])

    def format_element_dict(self, template_data_str):
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
        return template_data

    def parse_dict(self, element_dict):
        json_dict = {}
        for layer, layer_dict in element_dict.items():
            layer_dict_json = {str(k): v for k, v in layer_dict.items() if 'cyfunction' not in str(k)}
            json_dict[layer] = layer_dict_json
        return json_dict

    def get_tag_mapping(self, html_source):
        parser = MapItemToHtmlTagsParser(config='')
        pre_data = {PreDataJsonKey.TYPICAL_RAW_TAG_HTML: html_source, PreDataJsonKey.HTML_ELEMENT_DICT: {}, PreDataJsonKey.LLM_RESPONSE: {}}
        element_dict = parser.parse(pre_data)
        return element_dict[PreDataJsonKey.HTML_ELEMENT_DICT]

    def get_feature_by_element_dict(self, element_dict, position, depth=3):
        """获取指定位置及其三层子孙节点的属性和标签。

        参数:
            element_dict: 包含层级信息的字典
            position: 目标节点的位置列表

        返回:
            {"tags": tags_dict, "attrs": attrs_dict}: 分别包含标签和属性的字典
        """
        tags_dict = {}
        attrs_dict = {}
        # 从给定的深度开始，向下处理最多三层
        for layer in range(position[0], min(position[0] + 3, len(element_dict))):
            if layer not in element_dict:
                continue

            layer_num = layer  # 使用层级作为键
            tags_dict.setdefault(layer_num, [])
            attrs_dict.setdefault(layer_num, [])

            # 遍历当前层级的所有元素
            for element_key, element_value in element_dict[layer].items():
                # 从元组中提取信息
                tag_name = element_key[0]  # 第一个元素是标签名
                class_attr = element_key[1]  # 第二个元素是class属性
                id_attr = element_key[2]  # 第三个元素是id属性

                # 处理标签，跳过None值
                if tag_name is not None:
                    tag_str = f'<{tag_name}>'
                    tags_dict[layer_num].append(tag_str)

                # 处理属性 (优先使用class，其次是id)
                attr_value = class_attr if class_attr is not None else id_attr
                # 只有当属性值不为None时才添加
                if attr_value is not None:
                    attrs_dict[layer_num].append(attr_value)

        return {'tags': tags_dict, 'attrs': attrs_dict}

    def parse_tuple_key(self, key_str):
        if key_str.startswith('(') and key_str.endswith(')'):
            try:
                return eval(key_str)  # WARNING: eval is unsafe for untrusted data!
            except (SyntaxError, ValueError):
                return key_str  # Fallback if parsing fails
        return key_str

    def get_similarity(self, test_element_dict, position, element_dict):
        elem_feature = self.get_feature_by_element_dict(test_element_dict, position)
        template_feature = self.get_feature_by_element_dict(element_dict, position)
        layer_n = max(len(test_element_dict), len(element_dict))
        if elem_feature and template_feature:
            score = similarity(elem_feature, template_feature, layer_n=layer_n)
            if score > SIMILARITY_THRESHOLD:
                return True
            else:
                return False
        else:
            return False

    def parse(self, pre_data: PreDataJson) -> PreDataJson:
        html_source = pre_data[PreDataJsonKey.HTML_SOURCE]
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

        # 不要创建新实例，直接使用当前实例处理
        content, body = self.process(html_source)
        # 相似度计算
        if pre_data.get(PreDataJsonKey.TYPICAL_MAIN_HTML, None):
            template_main_html = pre_data[PreDataJsonKey.TYPICAL_MAIN_HTML]
            layer_n = max(len(template_data), len(self.template_data))
            feature1 = get_feature(template_main_html)
            feature2 = get_feature(body)
            layer_n = self.__get_max_width_layer(template_data)
            sim = similarity(feature1, feature2, layer_n=layer_n)
            if sim < SIMILARITY_THRESHOLD:
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

    def process(self, html_source: str) -> str:
        # 根据颜色删减html_source
        processed_html = self.drop_node_element(html_source, self.template_data)
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

    def get_color_element_dict(self, test_element_dict, template_element_dict):
        """根据template_element_dict给test_element_dict进行染色，染色逻辑基于节点位置相同.

        参数:
            test_element_dict: 需要染色的元素字典
            template_element_dict: 模板元素字典，用于参考染色

        返回:
            染色后的test_element_dict
        """
        colored_dict = test_element_dict.copy()

        # 遍历test_element_dict的每一层
        for layer in test_element_dict:
            if layer not in template_element_dict:
                continue

            # 遍历当前层的每个节点
            for test_key, test_value in test_element_dict[layer].items():
                test_position = [test_key[-2], test_key[-1]]  # 获取测试节点的位置

                # 在模板字典的同一层中寻找位置相同或相近的节点
                for template_key, template_value in template_element_dict[layer].items():
                    if isinstance(template_key, tuple) and len(template_key) >= 5:
                        template_position = [template_key[3], template_key[4]]  # 获取模板节点的位置

                        # 计算位置差异
                        position_diff = [test_position[0] - template_position[0],
                                         test_position[1] - template_position[1]]
                        # TODO 这里需要优化，如果位置相同或相近（差异在±1范围内），且标签相同，则染色
                        if ((-1 <= position_diff[0] <= 1 and -1 <= position_diff[1] <= 1) and test_key[0] == template_key[0]):  # 检查标签是否相同
                            # 进一步检查相似度
                            if self.get_similarity(test_element_dict, test_position, template_element_dict):
                                # 染色：使用模板中的颜色
                                colored_dict[layer][test_key] = list(test_value)
                                # 从template_value获取颜色值
                                if isinstance(template_value, list) and len(template_value) > 0:
                                    colored_dict[layer][test_key][0] = template_value[0]
        return colored_dict

    def find_blocks_drop(self, element, depth, element_dict, parent_keyy, parent_label):
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
        keyy = self.normalize_key((tag, class_tag, idd))
        # 获取element的当前子层的所有节点
        element_parent = element.getparent()
        current_layer_keys = set()
        if element_parent is None:
            current_layer_keys.add(keyy)
        else:
            for child in element_parent:
                child_key = self.normalize_key((child.tag, child.get('class'), child.get('id')))
                current_layer_keys.add(child_key)

        # 获取element的当前子层的所有节点
        element_parent = element.getparent()
        current_layer_keys = set()
        if element_parent is None:
            current_layer_keys.add(keyy)
        else:
            for child in element_parent:
                child_key = self.normalize_key((child.tag, child.get('class'), child.get('id')))
                current_layer_keys.add(child_key)

        # 匹配正文节点
        has_red = False
        layer_nodes_list = []
        layer_nodes_dict = dict()
        if class_tag == 'mw-editsection':
            print('test')
        for node_keyy, node_value in layer_nodes.items():
            node_parent_keyy = self.normalize_key(node_value[1])
            if node_parent_keyy is not None:
                node_parent_keyy = tuple(node_parent_keyy)
            node_label = node_value[0]
            norm_node_keyy = self.normalize_key(node_keyy[:3])
            if node_parent_keyy == parent_keyy and norm_node_keyy in current_layer_keys:
                layer_nodes_list.append((node_keyy[:3], node_label))
                if norm_node_keyy in layer_nodes_dict:
                    layer_nodes_dict[norm_node_keyy].append(node_label)
                else:
                    layer_nodes_dict[norm_node_keyy] = [node_label]

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
            self.find_blocks_drop(child, depth + 1, element_dict, keyy, label)

    def get_main_html_by_color_element_dict(self, root, color_element_dict):
        """根据染色的元素字典处理HTML，删除非红色的节点.

        参数:
            root: HTML元素树
            color_element_dict: 染色后的元素字典

        返回:
            处理后的HTML内容
        """
        self.find_blocks_drop(root, 0, color_element_dict, None, None)
        return element_to_html(root)

    def drop_node_element(self, html_source, element_dict):
        # 解析 HTML 内容
        ori_html = html_to_element(html_source)
        colored_element_dict = self.get_color_element_dict(self.test_element_dict, self.template_data)
        # 返回处理后的HTML和染色后的元素字典
        return self.get_main_html_by_color_element_dict(ori_html, colored_element_dict)

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
