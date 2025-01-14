from lxml import etree

from llm_web_kit.libs.html_utils import build_cc_element, replace_element
from llm_web_kit.pipeline.extractor.html.recognizer.cc_math.common import (
    CCMATH, CCMATH_INLINE, CCMATH_INTERLINE, EQUATION_INLINE,
    EQUATION_INTERLINE, text_strip)


def modify_tree(cm: CCMATH, math_render: str, o_html: str, node: etree._Element, parent: etree._Element):
    try:
        text = node.text

        equation_type, math_type = cm.get_equation_type(o_html)
        if equation_type == EQUATION_INLINE:
            new_tag = CCMATH_INLINE
            display = False
        elif equation_type == EQUATION_INTERLINE:
            new_tag = CCMATH_INTERLINE
            display = True
        else:
            raise ValueError(f'Unknown equation type: {equation_type}')

        if text and text_strip(text):
            wrapped_text = cm.wrap_math(r'{}'.format(text), display=display)
            new_span = build_cc_element(html_tag_name=new_tag, text=wrapped_text, tail=text_strip(node.tail), type=math_type, by=math_render, html=o_html)
            replace_element(node, new_span)

    except Exception as e:
        raise ValueError(f'Error processing script mathtex: {e}')
