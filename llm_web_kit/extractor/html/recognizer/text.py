import copy
import json
import re
import string
from typing import List, Tuple

from lxml import html
from lxml.html import HtmlElement
from overrides import override

from llm_web_kit.extractor.html.recognizer.recognizer import (
    BaseHTMLElementRecognizer, CCTag)
from llm_web_kit.libs.doc_element_type import DocElementType, ParagraphTextType
from llm_web_kit.libs.html_utils import (element_to_html_unescaped,
                                         html_to_element, process_sub_sup_tags)

special_symbols = [  # TODO 从文件读取
    '®',  # 注册商标符号
    '™',  # 商标符号
    '©',  # 版权符号
    '$',   # 美元符号
    '€',   # 欧元符号
    '£',   # 英镑符号
    '¥',   # 日元符号
    '₹',   # 印度卢比符号
    '∑',   # 求和符号
    '∞',   # 无穷大符号
    '√',   # 平方根符号
    '≠',   # 不等于符号
    '≤',   # 小于等于符号
    '•',   # 项目符号
    '¶',   # 段落符号
    '†',   # 匕首符号
    '‡',   # 双匕首符号
    '—',   # 长破折号
    '–',   # 短破折号
    '♥',   # 爱心符号
    '★',   # 星星符号
    '☀',   # 太阳符号
    '☁'    # 云符号
]

PARAGRAPH_SEPARATOR = '\n\n'

# 需要保留的html实体，例如：'>' 直接在markdown中无法渲染，需要替换为html实体
entities_map = {'>': 'gt'}

# 行内元素
inline_tags = {
    'a', 'abbr', 'acronym', 'b', 'bdo', 'big', 'br', 'button', 'cite', 'code',
    'dfn', 'em', 'i', 'img', 'input', 'kbd', 'label', 'map', 'object', 'q',
    'samp', 'script', 'select', 'small', 'span', 'strong', 'sub', 'sup',
    'textarea', 'time', 'var', 'u', 's', 'code', 'cccode-inline', 'ccmath-inline',
    'marked-tail', 'marked-text','math','mspace'
}


class TextParagraphRecognizer(BaseHTMLElementRecognizer):
    """解析文本段落元素."""

    @override
    def to_content_list_node(self, base_url: str, parsed_content: HtmlElement, raw_html_segment: str) -> dict:
        """
        把文本段落元素转换为content list node.
        Args:
            base_url:
            parsed_content: 可能是字符串或HtmlElement对象
            raw_html_segment:

        Returns:

        """
        # 如果是字符串则转换为HtmlElement，否则直接使用
        el = parsed_content
        node = {
            'type': DocElementType.PARAGRAPH,
            'raw_content': raw_html_segment,
            'content': json.loads(el.text),
        }
        return node

    @override
    def recognize(self, base_url:str, main_html_lst: List[Tuple[HtmlElement | str, HtmlElement | str]], raw_html:str) -> List[Tuple[HtmlElement, HtmlElement]]:
        """父类，解析文本段落元素.

        Args:
            base_url: str: 基础url
            main_html_lst: main_html在一层一层的识别过程中，被逐步分解成不同的元素
            raw_html: 原始完整的html

        Returns:
        """
        new_html_lst = []
        for html_element, raw_html_element in main_html_lst:
            # 如果是字符串则转换为 HtmlElement
            if self.is_cc_html(html_element):
                new_html_lst.append((html_element, raw_html_element))
            else:
                lst = list(self.__extract_paragraphs(html_element))
                new_lst = self.__to_cctext_lst(lst)
                new_html_lst.extend(new_lst)
        return new_html_lst

    def __to_cctext_lst(self, lst: List[Tuple[HtmlElement | str, HtmlElement | str]]) -> List[Tuple[HtmlElement, HtmlElement]]:
        """将lst[Element, raw_html] 进行处理. 提出Element里的文字，做成<<cctext>>标签.

        Args:
            lst: List[Tuple[HtmlElement | str, HtmlElement | str]]: Element和raw_html组成的列表
        """
        new_lst = []
        for el, raw_html in lst:
            # 如果是字符串则转换为 HtmlElement
            el_element = html_to_element(el) if isinstance(el, str) else el
            raw_html_element = html_to_element(raw_html) if isinstance(raw_html, str) else raw_html

            para_text = self.__get_paragraph_text(el_element)
            if para_text:
                cctext_el = self._build_cc_element(CCTag.CC_TEXT, json.dumps(para_text, ensure_ascii=False, indent=4), '', html=element_to_html_unescaped(raw_html_element))
                new_lst.append((cctext_el, raw_html_element))
        return new_lst

    def replace_entities(self, text, entities_map):
        """使用正则表达式同时替换文本中的多个特定字符为其对应的HTML实体。

        :param text: 需要处理的文本。
        :param entities_map: 一个字典，键是需要替换的字符，值是对应的HTML实体名
        :return: 替换后的文本。
        """
        # 创建正则表达式模式，匹配所有需要替换的字符
        rx = re.compile('|'.join(re.escape(str(key)) for key in entities_map.keys()))

        def one_xlat(match):
            """回调函数，用于将匹配到的字符替换为对应的HTML实体。"""
            return f'&{entities_map[match.group(0)]};'

        return rx.sub(one_xlat, text)

    def __combine_text(self, text1:str, text2:str, lang='en') -> str:
        """将两段文本合并，中间加空格.

        Args:
            text1: str: 第一段文本
            text2: str: 第二段文本
            lang: str: 语言  TODO 实现根据语言连接文本的不同方式, 还有就是一些特殊符号开头的连接不加空格。
        """
        text1 = text1.strip(' ') if text1 else ''
        text2 = text2.strip(' ') if text2 else ''
        if lang == 'zh':
            txt = text1 + text2
            return self.replace_entities(txt.strip(), entities_map)
        else:
            words_sep = '' if text2[0] in string.punctuation or text2[0] in special_symbols else ' '
            txt = text1 + words_sep + text2
            return self.replace_entities(txt.strip(), entities_map)

    def __get_paragraph_text(self, root: HtmlElement) -> List[dict]:
        """
        获取段落全部的文本.
        对于段落里的行内公式<equation-inline>需要特定处理，转换为段落格式：
        [
          {"c":"content text", "t":"text"},
          {"c": "equation text", "t":"equation"},
          {"c":"content text", "t":"text"}
        ]

        Args:
            el: 代表一个段落的html元素
        """
        para_text = []

        def __get_paragraph_text_recusive(el: HtmlElement, text: str) -> str:

            # 标记当前元素是否是sub或sup类型
            is_sub_sup = el.tag == 'sub' or el.tag == 'sup'

            if el.tag == CCTag.CC_MATH_INLINE:
                if text:
                    para_text.append({'c': text, 't': ParagraphTextType.TEXT})
                    text = ''
                para_text.append({'c': el.text, 't': ParagraphTextType.EQUATION_INLINE})
            elif el.tag == CCTag.CC_CODE_INLINE:
                if text:
                    para_text.append({'c': text, 't': ParagraphTextType.TEXT})
                    text = ''
                para_text.append({'c': el.text, 't': ParagraphTextType.CODE_INLINE})
            elif el.tag in ['br']:
                text += PARAGRAPH_SEPARATOR  # TODO 这个地方直接加换行是错误点做法，需要利用数据结构来保证段落。
            elif el.tag == 'sub' or el.tag == 'sup':
                text = process_sub_sup_tags(el, text, recursive=False)
            else:
                if el.text and el.text.strip():
                    text = self.__combine_text(text, el.text.strip())
                for child in el:
                    text = __get_paragraph_text_recusive(child, text)

            # 处理尾部文本
            if el.tail and el.tail.strip():
                if is_sub_sup:
                    text += el.tail
                else:
                    text = self.__combine_text(text, el.tail.strip())

            return text

        if final := __get_paragraph_text_recusive(root, ''):
            para_text.append({'c': final, 't': ParagraphTextType.TEXT})

        return para_text

    def __extract_paragraphs(self, root: HtmlElement):
        """解析HtmlElement为段落元素列表.

        :param root: 根元素
        :return: 段落元素列表
        """

        def is_block_element(node) -> bool:
            """如果标签不在内联元素集合中，默认为块级元素。 但是，如果一个内联元素包含块级元素，则该内联元素被视为块级元素。"""
            if node.tag in inline_tags:
                return any(is_block_element(child) for child in node.iterchildren())
            return isinstance(node, html.HtmlElement)

        def has_block_children(node) -> bool:
            return any(is_block_element(child) for child in node.iterchildren())

        def clone_structure(path: List[html.HtmlElement]) -> Tuple[html.HtmlElement, html.HtmlElement]:
            if not path:
                raise ValueError('Path cannot be empty')
            root = html.Element(path[0].tag, **path[0].attrib)
            current = root
            for node in path[1:-1]:
                new_node = html.Element(node.tag, **node.attrib)
                current.append(new_node)
                current = new_node
            last_node = html.Element(path[-1].tag, **path[-1].attrib)
            current.append(last_node)
            return root, last_node

        paragraphs = []

        def process_node(node: html.HtmlElement, path: List[html.HtmlElement]):
            current_path = path + [node]
            inline_content = []  # 累积内联内容和未包裹文本

            # 首先处理父节点下的直接文本内容（node.text）
            if node.text and node.text.strip():
                inline_content.append(('direct_text', node.text.strip()))

            # 处理所有子节点
            for child in node:
                if is_block_element(child):
                    # 遇到块级元素，先处理之前累积的内容
                    if inline_content:
                        try:
                            root, last_node = clone_structure(current_path)
                            merge_inline_content(last_node, inline_content)
                            paragraphs.append(root)
                        except ValueError:
                            pass
                        inline_content = []

                    # 处理块级元素本身
                    if not has_block_children(child):
                        # 没有子块级元素，作为独立段落
                        try:
                            root, last_node = clone_structure(current_path + [child])
                            last_node.text = child.text if child.text else None
                            for grandchild in child:
                                last_node.append(copy.deepcopy(grandchild))
                            paragraphs.append(root)
                        except ValueError:
                            pass
                    else:
                        # 有子块级元素，递归处理
                        process_node(child, current_path)

                    # 处理当前块级元素的tail文本（与块级元素同级）
                    if child.tail and child.tail.strip():
                        inline_content.append(('tail_text', child.tail.strip()))
                else:
                    # 非块级元素
                    inline_content.append(('element', child))
                    # 处理非块级元素的tail文本
                    if child.tail and child.tail.strip():
                        inline_content.append(('tail_text', child.tail.strip()))

            # 处理剩余的内联内容（没有更多块级元素的情况）
            if inline_content:
                try:
                    root, last_node = clone_structure(current_path)
                    merge_inline_content(last_node, inline_content)
                    paragraphs.append(root)
                except ValueError:
                    pass

        def merge_inline_content(parent: html.HtmlElement, content_list: List[Tuple[str, str]]):
            """将inline_content列表中的内容合并到给定的parent节点中。

            :param parent: 目标父节点
            :param content_list: 包含('direct_text'|'tail_text'|'element', content)元组的列表
            """
            last_inserted = None
            for item_type, item in content_list:
                if item_type in ('direct_text', 'tail_text'):
                    if last_inserted is None:
                        if not parent.text:
                            parent.text = item
                        else:
                            parent.text += ' ' + item
                    else:
                        if last_inserted.tail is None:
                            last_inserted.tail = item
                        else:
                            last_inserted.tail += ' ' + item
                else:  # element
                    parent.append(copy.deepcopy(item))
                    last_inserted = item

        process_node(root, [])

        unique_paragraphs = []
        for p in paragraphs:
            unique_paragraphs.append((p, p))

        return unique_paragraphs
