import html
import re
import string
from copy import deepcopy

from lxml.html import HtmlElement, HTMLParser, fromstring, tostring

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


def html_to_element(html:str) -> HtmlElement:
    """构建html树.

    Args:
        html: str: 完整的html源码

    Returns:
        element: lxml.html.HtmlElement: element
    """
    parser = HTMLParser(collect_ids=False, encoding='utf-8', remove_comments=True, remove_pis=True)
    # 将 HTML 字符串编码为字节类型, 兼容html中有 XML 声明（如 <?xml version="1.0" encoding="utf-8"?>）
    html_bytes = html.encode('utf-8')
    root = fromstring(html_bytes, parser=parser)
    standalone = deepcopy(root)  # 通过拷贝才能去掉自动加入的<html><body>等标签， 非常奇怪的表现。
    return standalone


def element_to_html(element : HtmlElement) -> str:
    """将element转换成html字符串.

    Args:
        element: lxml.html.HtmlElement: element

    Returns:
        str: html字符串
    """
    s = tostring(element, encoding='utf-8').decode()
    return s


def element_to_html_unescaped(element : HtmlElement) -> str:
    """将element转换成html字符串并保持标签不被转义.

    Args:
        element: lxml.html.HtmlElement: element

    Returns:
        str: html字符串
    """
    s = element_to_html(element)
    return html.unescape(s)


def build_cc_element(html_tag_name: str, text: str, tail: str, **kwargs) -> HtmlElement:
    """构建cctitle的html. 例如：<cctitle level=1>标题1</cctitle>

    Args:
        html_tag_name: str: html标签名称，例如 'cctitle'
        text: str: 标签的文本内容
        tail: str: 标签后的文本内容
        **kwargs: 标签的其他属性，例如 level='1', html='<h1>标题</h1>' 等

    Returns:
        str: cctitle的html
    """
    attrib = {k:str(v) for k,v in kwargs.items()}
    parser = HTMLParser(collect_ids=False, encoding='utf-8', remove_comments=True, remove_pis=True)
    cc_element = parser.makeelement(html_tag_name, attrib)
    cc_element.text = text
    cc_element.tail = tail
    return cc_element


def get_element_text(element: HtmlElement) -> str:
    """
    获取这个节点下，包括子节点的所有文本.
    Args:
        element:

    Returns:

    """
    text = ''.join(element.itertext())
    return text


def replace_element(old_element: HtmlElement, new_element: HtmlElement) -> None:
    """替换element为cc_element.

    Args:
        old_element: HtmlElement: 要替换的元素
        new_element: HtmlElement: 替换的元素
    """
    if old_element.getparent() is not None:
        old_element.getparent().replace(old_element, new_element)
    else:
        old_element.tag = new_element.tag
        old_element.text = new_element.text
        for k,_ in old_element.attrib.items():
            del old_element.attrib[k]
        for k, v in new_element.attrib.items():
            old_element.attrib[k] = v
        old_element.tail = new_element.tail
        for child in new_element:
            old_element.append(child)


def iter_node(element: HtmlElement):
    """迭代html树.

    Args:
        element: lxml.html.HtmlElement: html树

    Returns:
        generator: 迭代html树
    """
    yield element
    for sub_element in element:
        if isinstance(sub_element, HtmlElement):
            yield from iter_node(sub_element)


def _escape_table_cell(text: str) -> str:
    """转义表格单元格中的特殊字符.

    比如 |、内容中的\n等
    """
    # 首先处理换行符，将其替换为空格
    text = re.sub(r'[\r\n]+', ' ', text)
    # 转义竖线和点号，避免与markdown表格语法冲突
    escaped = text.replace('|', '\\|')
    return escaped


def html_to_markdown_table(table_html_source: str) -> str:
    """把html代码片段转换成markdown表格.

    Args:
        table_html_source: 被<table>标签包裹的html代码片段(含<table>标签)

    Returns: 如果这个表格内没有任何文字性内容，则返回空字符串
    """
    # 解析HTML
    table_el = html_to_element(table_html_source)
    rows = table_el.xpath('.//tr')
    if not rows:
        return ''

    # 确定最大列数
    max_cols = 0
    for row in rows:
        cols = row.xpath('.//th | .//td')
        max_cols = max(max_cols, len(cols))

    if max_cols == 0:
        return ''
    markdown_table = []
    first_row = rows[0]
    # 检查第一行是否是表头并获取表头内容
    first_row_tags = first_row.xpath('.//th | .//td')
    if not first_row_tags:
        # 如果第一行没有td/th，则取整行内容作为表头
        headers = [_escape_table_cell(first_row.text_content().strip())]
    else:
        headers = [_escape_table_cell(tag.text_content().strip()) for tag in first_row_tags]
    # 如果表头存在，添加表头和分隔符，并保证表头与最大列数对齐
    if headers:
        while len(headers) < max_cols:
            headers.append('')  # 补充空白表头
        markdown_table.append('| ' + ' | '.join(headers) + ' |')
        markdown_table.append('|---' * max_cols + '|')
    else:
        # 如果没有明确的表头，创建默认表头
        default_headers = [''] * max_cols
        markdown_table.append('| ' + ' | '.join(default_headers) + ' |')
        markdown_table.append('|---' * max_cols + '|')

    # 添加表格内容，跳过已被用作表头的第一行（如果有的话）
    for row in rows[1:]:
        cells = row.xpath('.//td | .//th')
        if not cells:  # 无td/th时取整行内容，放到第一个单元格
            columns = [_escape_table_cell(row.text_content().strip())]
        else:
            columns = [_escape_table_cell(cell.text_content().strip()) for cell in cells]
        while len(columns) < max_cols:
            columns.append('')
        markdown_table.append('| ' + ' | '.join(columns) + ' |')

    md_str = '\n'.join(markdown_table)
    return md_str.strip()


def table_cells_count(table_html_source: str) -> int:
    """获取表格的单元格数量. 当只有1个单元格时，这个table就要被当做普通的一个段落处理。 只计算有实际内容的单元格数量。

    Args:
        table_html_source: str: 被<table>标签包裹的html代码片段(含<table>标签)

    Returns:
        int: 有内容的单元格数量
    """
    table_el = html_to_element(table_html_source)
    cell_count = 0

    # 获取所有行
    rows = table_el.xpath('.//tr')
    for row in rows:
        # 先检查是否有 td 或 th
        cells = row.xpath('.//td | .//th')
        if cells:
            # 如果有 td 或 th，计算有内容的单元格
            cell_count += sum(1 for cell in cells if cell.text_content().strip())
        else:
            # 如果没有 td 或 th，检查 tr 是否直接包含内容
            row_content = row.text_content().strip()
            if row_content:
                cell_count += 1

    return cell_count


def convert_html_to_entity(html_source) -> str:
    """html中的特殊字符转成实体标记."""
    table_entity = html.escape(html_source)
    return table_entity


def convert_html_entity_to_str(html_str):
    """将HTML实体转换回原始字符."""
    result = html.unescape(html_str)
    return result


def remove_element(element: HtmlElement):
    """删除节点.

    删除节点时，保留节点后的tail文本

    Args:
        element: HtmlElement
    """
    parent = element.getparent()
    if parent is None:
        return

    if element.tail:
        previous = element.getprevious()
        if previous is None:
            parent.text = (parent.text or '') + element.tail
        else:
            previous.tail = (previous.tail or '') + element.tail
    parent.remove(element)


def extract_magic_html(html, base_url, page_layout_type):
    """提取magic html.

    Args:
        html: str: html字符串
        base_url: str: 基础url
        page_layout_type: str: 页面布局类型
    """
    from llm_web_kit.extractor.html.extractor import HTMLFileFormatExtractor

    extractor = HTMLFileFormatExtractor({})
    try:
        main_html, _, _ = extractor._extract_main_html(html, base_url, page_layout_type)
        return main_html
    except Exception as e:
        from llm_web_kit.exception.exception import MagicHtmlExtractorException
        raise MagicHtmlExtractorException(f'extract_magic_html error: {e}')


def combine_text(text1: str, text2: str, lang='en') -> str:
    """将两段文本合并，中间加空格.

    Args:
        text1: str: 第一段文本
        text2: str: 第二段文本
        lang: str: 语言
    """
    text1 = text1.strip(' ') if text1 else ''
    text2 = text2.strip(' ') if text2 else ''
    if lang == 'zh':
        txt = text1 + text2
        return txt.strip()
    else:
        # 防止字符串为空导致索引错误
        words_sep = '' if text2 and (text2[0] in string.punctuation or text2[0] in special_symbols) else ' '
        txt = text1 + words_sep + text2
        return txt.strip()


def process_sub_sup_tags(element: HtmlElement, current_text: str = '', lang='en', recursive=True) -> str:
    """处理HTML元素中的sub/sup标签，将其转换为GitHub Flavored Markdown格式.

    此函数可以处理直接的sub/sup标签元素，也可以处理包含sub/sup标签的父元素。
    对于sub/sup相关内容，不进行strip操作，直接拼接文本。
    对于非sub/sup相关内容，使用combine_text进行文本拼接。

    Args:
        element: HtmlElement: 要处理的HTML元素
        current_text: str: 当前已经处理的文本，默认为空字符串
        lang: str: 语言，用于文本合并时的空格处理，默认为'en'
        recursive: bool: 是否递归处理子元素，默认为True

    Returns:
        str: 处理后的文本，包含GitHub Flavored Markdown格式的上标和下标
    """
    # 判断是否是sub/sup上下文
    is_sub_sup_context = element.tag in ('sub', 'sup') or bool(element.xpath('.//sub | .//sup'))

    # 直接处理当前元素是sub或sup的情况
    if element.tag == 'sub' or element.tag == 'sup':
        marker = element.tag
        content = element.text or ''

        # 处理所有子元素
        for child in element:
            if child.tag in ('sub', 'sup'):
                # 对于嵌套的sub/sup标签，保留它们的标签结构
                child_result = process_sub_sup_tags(child, '', lang, True)
                content += child_result
            else:
                # 处理常规子元素，如span等
                if child.text:
                    content += child.text

                # 递归处理子元素的子元素
                for grandchild in child:
                    if grandchild.tag in ('sub', 'sup'):
                        content += process_sub_sup_tags(grandchild, '', lang, True)

                # 处理子元素的尾部文本
                if child.tail:
                    content += child.tail

        # 规范化空白并构建最终结果
        # content = re.sub(r'\s+', ' ', content).strip()
        result = f'{current_text.rstrip()}<{marker}>{content}</{marker}>'
        return result

    # 检查是否包含sub或sup子元素，如果不包含且不是sub/sup上下文，则按照普通文本处理
    if not recursive:
        if is_sub_sup_context:
            return current_text  # 不strip
        else:
            return combine_text(current_text, '', lang)

    has_sub_sup = element.xpath('.//sub | .//sup')
    if not has_sub_sup and not is_sub_sup_context:
        return combine_text(current_text, '', lang)

    result = current_text
    if element.text:
        if is_sub_sup_context:
            result += element.text
        else:
            result = combine_text(result, element.text, lang)

    # 处理所有子元素及其尾部文本
    for child in element:
        child_result = process_sub_sup_tags(child, '', lang, recursive)
        if child_result:
            if is_sub_sup_context:
                result += child_result
            else:
                result = combine_text(result, child_result, lang)

        # 添加尾部文本
        if child.tail:
            if is_sub_sup_context:
                result += child.tail
            else:
                result = combine_text(result, child.tail, lang)

    return result
