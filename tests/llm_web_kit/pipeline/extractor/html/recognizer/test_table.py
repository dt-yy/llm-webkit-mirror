import unittest
from pathlib import Path

from llm_web_kit.pipeline.extractor.html.recognizer.table import \
    TableRecognizer

TEST_CASES = [
    {
        'input': (
            'assets/recognizer/table.html',
            'assets/recognizer/table_exclude.html',
            'assets/recognizer/only_table.html',
            'assets/recognizer/table_simple_compex.html',
        ),
        'expected': [
            ('<cccode>hello</cccode>', '<code>hello</code>'),
            (
                '<html><body><p>段落2</p></body></html>',
                '<html><body><p>段落2</p></body></html>',
            ),
            (
                '<html><body><cctable type="complex" html="<table><tr><td rowspan="2">1</td><td>2</td></tr><tr><td>3</td></tr></table>">\'<tr><td rowspan="2">1</td><td>2</td></tr><tr><td>3</td></tr>\'</cctable></body></html>',
                '<table><tr><td rowspan="2">1</td><td>2</td></tr><tr><td>3</td></tr></table>',
            ),
            (
                '<html><body><p>段落2</p></body></html>',
                '<html><body><p>段落2</p></body></html>',
            ),
            (
                [
                    (
                        '<html><head><meta><title>Title</title></head><body><h1>Heading 1</h1><p>Paragraph 1</p><div><img><p>Paragraph 2</p></div></body></html>',
                        '<html><head><meta><title>Title</title></head><body><h1>Heading 1</h1><p>Paragraph 1</p><div><img><p>Paragraph 2</p></div></body></html>',
                    ),
                    (
                        '<html><body><cctable table_type="simple" html="<table>\n    <tr>\n        <td>1</td>\n        <td>2</td>\n    </tr>\n    <tr>\n        <td>3</td>\n        <td>4</td>\n    </tr>\n</table>\n\n"><tr>\n        <td>1</td>\n        <td>2</td>\n    </tr>\n    </cctable></body></html>',
                        '<table>\n    <tr>\n        <td>1</td>\n        <td>2</td>\n    </tr>\n    <tr>\n        <td>3</td>\n        <td>4</td>\n    </tr>\n</table>\n\n',
                    ),
                    (
                        '<html><body><div><span><cctable table_type="complex" html=\'<table>\n        <tr>\n            <td rowspan="2">1</td>\n            <td>2</td>\n            <td>3</td>\n        </tr>\n        <tr>\n            <td colspan="2">4</td>\n        </tr>\n        <tr>\n            <td>5</td>\n            <td>6</td>\n            <td>7</td>\n        </tr>\n    </table>\n    \'><tr>\n            <td rowspan="2">1</td>\n            <td>2</td>\n            <td>3</td>\n        </tr>\n        </cctable></span></div></body></html>',
                        '<table>\n        <tr>\n            <td rowspan="2">1</td>\n            <td>2</td>\n            <td>3</td>\n        </tr>\n        <tr>\n            <td colspan="2">4</td>\n        </tr>\n        <tr>\n            <td>5</td>\n            <td>6</td>\n            <td>7</td>\n        </tr>\n    </table>\n    ',
                    ),
                    (
                        "<html><body><div><span></span></div><ul><li>1</li><li>2</li></ul><ul><li>1\n        <ul><li>1.1</li><li>1.2</li></ul></li><li>2\n        <ul><li>2.1</li><li>2.2</li></ul></li></ul><math><mi>x</mi><mo>=</mo><mrow><mfrac><mrow><mo>−</mo><mi>b</mi><mo>±</mo><msqrt><msup><mi>b</mi><mn>2</mn></msup><mo>−</mo><mn>4</mn><mi>a</mi><mi>c</mi></msqrt></mrow><mrow><mn>2</mn><mi>a</mi></mrow></mfrac></mrow><mtext>.</mtext></math><pre><code>const Prism = require('prismjs');\n\n    // The code snippet you want to highlight, as a string\n    const code = var data = 1;;\n\n    // Returns a highlighted HTML string\n    const html = Prism.highlight(code, Prism.languages.javascript, 'javascript');</code></pre></body></html>",
                        "<html><body><div><span></span></div><ul><li>1</li><li>2</li></ul><ul><li>1\n        <ul><li>1.1</li><li>1.2</li></ul></li><li>2\n        <ul><li>2.1</li><li>2.2</li></ul></li></ul><math><mi>x</mi><mo>=</mo><mrow><mfrac><mrow><mo>−</mo><mi>b</mi><mo>±</mo><msqrt><msup><mi>b</mi><mn>2</mn></msup><mo>−</mo><mn>4</mn><mi>a</mi><mi>c</mi></msqrt></mrow><mrow><mn>2</mn><mi>a</mi></mrow></mfrac></mrow><mtext>.</mtext></math><pre><code>const Prism = require('prismjs');\n\n    // The code snippet you want to highlight, as a string\n    const code = var data = 1;;\n\n    // Returns a highlighted HTML string\n    const html = Prism.highlight(code, Prism.languages.javascript, 'javascript');</code></pre></body></html>",
                    ),
                ]
            ),
        ],
    }
]

base_dir = Path(__file__).parent


class TestTableRecognizer(unittest.TestCase):
    def setUp(self):
        self.rec = TableRecognizer()

    def test_involve_cctale(self):
        for test_case in TEST_CASES:
            raw_html_path = base_dir.joinpath(test_case['input'][0])
            base_url = test_case['input'][1]
            raw_html = raw_html_path.read_text()
            parts = self.rec.recognize(base_url, [(raw_html, raw_html)], raw_html)
            self.assertEqual(len(parts), 4)

    def test_not_involve_table(self):
        """不包含表格."""
        for test_case in TEST_CASES:
            raw_html_path = base_dir.joinpath(test_case['input'][1])
            base_url = test_case['input'][1]
            raw_html = raw_html_path.read_text()
            parts = self.rec.recognize(base_url, [(raw_html, raw_html)], raw_html)
            self.assertEqual(len(parts), 1)

    def test_only_involve_table(self):
        """只包含表格的Html解析."""
        for test_case in TEST_CASES:

            raw_html_path = base_dir.joinpath(test_case['input'][2])
            base_url = test_case['input'][1]
            raw_html = raw_html_path.read_text()
            parts = self.rec.recognize(base_url, [(raw_html, raw_html)], raw_html)
            self.assertEqual(len(parts), 2)

    def test_simple_complex_table(self):
        """包含简单和复杂table."""
        for test_case in TEST_CASES:
            raw_html_path = base_dir.joinpath(test_case['input'][3])
            base_url = test_case['input'][1]
            raw_html = raw_html_path.read_text(encoding='utf-8')
            parts = self.rec.recognize(base_url, [(raw_html, raw_html)], raw_html)
            assert (
                parts[1][0]
                == '<html><body><cctable table_type="simple" html="&lt;table&gt;\n    &lt;tr&gt;\n        &lt;td&gt;1&lt;/td&gt;\n        &lt;td&gt;2&lt;/td&gt;\n    &lt;/tr&gt;\n    &lt;tr&gt;\n        &lt;td&gt;3&lt;/td&gt;\n        &lt;td&gt;4&lt;/td&gt;\n    &lt;/tr&gt;\n&lt;/table&gt;\n\n">&lt;tr&gt;\n        &lt;td&gt;1&lt;/td&gt;\n        &lt;td&gt;2&lt;/td&gt;\n    &lt;/tr&gt;\n    </cctable></body></html>'
            )
            assert (
                parts[2][0]
                == '<html><body><div><span><cctable table_type="complex" html=\'&lt;table&gt;\n        &lt;tr&gt;\n            &lt;td rowspan="2"&gt;1&lt;/td&gt;\n            &lt;td&gt;2&lt;/td&gt;\n            &lt;td&gt;3&lt;/td&gt;\n        &lt;/tr&gt;\n        &lt;tr&gt;\n            &lt;td colspan="2"&gt;4&lt;/td&gt;\n        &lt;/tr&gt;\n        &lt;tr&gt;\n            &lt;td&gt;5&lt;/td&gt;\n            &lt;td&gt;6&lt;/td&gt;\n            &lt;td&gt;7&lt;/td&gt;\n        &lt;/tr&gt;\n    &lt;/table&gt;\n    \'>&lt;tr&gt;\n            &lt;td rowspan="2"&gt;1&lt;/td&gt;\n            &lt;td&gt;2&lt;/td&gt;\n            &lt;td&gt;3&lt;/td&gt;\n        &lt;/tr&gt;\n        </cctable></span></div></body></html>'
            )

    def test_table_to_content_list_node_simple(self):
        """测试table的 to content list node方法."""
        for test_case in TEST_CASES:
            raw_html_path = base_dir.joinpath(test_case['input'][3])
            base_url = test_case['input'][1]
            raw_html = raw_html_path.read_text(encoding='utf-8')
            parsed_content = '<cctable table_type="simple" html="&lt;table&gt;\n    &lt;tr&gt;\n        &lt;td&gt;1&lt;/td&gt;\n        &lt;td&gt;2&lt;/td&gt;\n    &lt;/tr&gt;\n    &lt;tr&gt;\n        &lt;td&gt;3&lt;/td&gt;\n        &lt;td&gt;4&lt;/td&gt;\n    &lt;/tr&gt;\n&lt;/table&gt;\n\n">&lt;tr&gt;\n        &lt;td&gt;1&lt;/td&gt;\n        &lt;td&gt;2&lt;/td&gt;\n    &lt;/tr&gt;\n    </cctable>'
            result = self.rec.to_content_list_node(base_url, parsed_content, raw_html)
            assert result == {
                'type': 'table',
                'raw_content': '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <title>Title</title>\n</head>\n<body>\n\n<!-- Path: 2.html -->\n\n<h1>Heading 1</h1>\n<p>Paragraph 1</p>\n<div>\n    <img alt="image-alt" title="image-title" src="test.png" />\n    <p>Paragraph 2</p>\n</div>\n\n<!-- 简单table -->\n<table>\n    <tr>\n        <td>1</td>\n        <td>2</td>\n    </tr>\n    <tr>\n        <td>3</td>\n        <td>4</td>\n    </tr>\n</table>\n\n<div>\n    <span>\n        <!-- 复杂table -->\n    <table>\n        <tr>\n            <td rowspan="2">1</td>\n            <td>2</td>\n            <td>3</td>\n        </tr>\n        <tr>\n            <td colspan="2">4</td>\n        </tr>\n        <tr>\n            <td>5</td>\n            <td>6</td>\n            <td>7</td>\n        </tr>\n    </table>\n    </span>\n</div>\n\n<!-- 简单list -->\n<ul>\n    <li>1</li>\n    <li>2</li>\n</ul>\n\n<!-- 列表项里有子列表 -->\n<ul>\n    <li>1\n        <ul>\n            <li>1.1</li>\n            <li>1.2</li>\n        </ul>\n    </li>\n    <li>2\n        <ul>\n            <li>2.1</li>\n            <li>2.2</li>\n        </ul>\n    </li>\n</ul>\n\n<!-- 数学公式 -->\n<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">\n    <mi>x</mi>\n    <mo>=</mo>\n    <mrow>\n      <mfrac>\n        <mrow>\n          <mo>&#x2212;</mo>\n          <mi>b</mi>\n          <mo>&#x00B1;</mo>\n          <msqrt>\n            <msup>\n              <mi>b</mi>\n              <mn>2</mn>\n            </msup>\n            <mo>&#x2212;</mo>\n            <mn>4</mn>\n            <mi>a</mi>\n            <mi>c</mi>\n          </msqrt>\n        </mrow>\n        <mrow>\n          <mn>2</mn>\n          <mi>a</mi>\n        </mrow>\n      </mfrac>\n    </mrow>\n    <mtext>.</mtext>\n  </math>\n\n<!-- 代码 -->\n<pre><code class="language-js">const Prism = require(\'prismjs\');\n\n    // The code snippet you want to highlight, as a string\n    const code = `var data = 1;`;\n\n    // Returns a highlighted HTML string\n    const html = Prism.highlight(code, Prism.languages.javascript, \'javascript\');</code></pre>\n\n</body>\n</html>\n',
                'content': {
                    'html': '<tr>\n        <td>1</td>\n        <td>2</td>\n    </tr>\n    ',
                    'is_complex': 'simple',
                },
            }

    def test_table_to_content_list_node_complex(self):
        """测试table的 complex table to content list node方法."""
        for test_case in TEST_CASES:
            raw_html_path = base_dir.joinpath(test_case['input'][3])
            base_url = test_case['input'][1]
            raw_html = raw_html_path.read_text(encoding='utf-8')
            parsed_content = '<cctable table_type="complex" html=\'&lt;table&gt;\n        &lt;tr&gt;\n            &lt;td rowspan="2"&gt;1&lt;/td&gt;\n            &lt;td&gt;2&lt;/td&gt;\n            &lt;td&gt;3&lt;/td&gt;\n        &lt;/tr&gt;\n        &lt;tr&gt;\n            &lt;td colspan="2"&gt;4&lt;/td&gt;\n        &lt;/tr&gt;\n        &lt;tr&gt;\n            &lt;td&gt;5&lt;/td&gt;\n            &lt;td&gt;6&lt;/td&gt;\n            &lt;td&gt;7&lt;/td&gt;\n        &lt;/tr&gt;\n    &lt;/table&gt;\n    \'>&lt;tr&gt;\n            &lt;td rowspan="2"&gt;1&lt;/td&gt;\n            &lt;td&gt;2&lt;/td&gt;\n            &lt;td&gt;3&lt;/td&gt;\n        &lt;/tr&gt;\n        </cctable>'
            result = self.rec.to_content_list_node(base_url, parsed_content, raw_html)
            assert result == {
                'type': 'table',
                'raw_content': '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <title>Title</title>\n</head>\n<body>\n\n<!-- Path: 2.html -->\n\n<h1>Heading 1</h1>\n<p>Paragraph 1</p>\n<div>\n    <img alt="image-alt" title="image-title" src="test.png" />\n    <p>Paragraph 2</p>\n</div>\n\n<!-- 简单table -->\n<table>\n    <tr>\n        <td>1</td>\n        <td>2</td>\n    </tr>\n    <tr>\n        <td>3</td>\n        <td>4</td>\n    </tr>\n</table>\n\n<div>\n    <span>\n        <!-- 复杂table -->\n    <table>\n        <tr>\n            <td rowspan="2">1</td>\n            <td>2</td>\n            <td>3</td>\n        </tr>\n        <tr>\n            <td colspan="2">4</td>\n        </tr>\n        <tr>\n            <td>5</td>\n            <td>6</td>\n            <td>7</td>\n        </tr>\n    </table>\n    </span>\n</div>\n\n<!-- 简单list -->\n<ul>\n    <li>1</li>\n    <li>2</li>\n</ul>\n\n<!-- 列表项里有子列表 -->\n<ul>\n    <li>1\n        <ul>\n            <li>1.1</li>\n            <li>1.2</li>\n        </ul>\n    </li>\n    <li>2\n        <ul>\n            <li>2.1</li>\n            <li>2.2</li>\n        </ul>\n    </li>\n</ul>\n\n<!-- 数学公式 -->\n<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">\n    <mi>x</mi>\n    <mo>=</mo>\n    <mrow>\n      <mfrac>\n        <mrow>\n          <mo>&#x2212;</mo>\n          <mi>b</mi>\n          <mo>&#x00B1;</mo>\n          <msqrt>\n            <msup>\n              <mi>b</mi>\n              <mn>2</mn>\n            </msup>\n            <mo>&#x2212;</mo>\n            <mn>4</mn>\n            <mi>a</mi>\n            <mi>c</mi>\n          </msqrt>\n        </mrow>\n        <mrow>\n          <mn>2</mn>\n          <mi>a</mi>\n        </mrow>\n      </mfrac>\n    </mrow>\n    <mtext>.</mtext>\n  </math>\n\n<!-- 代码 -->\n<pre><code class="language-js">const Prism = require(\'prismjs\');\n\n    // The code snippet you want to highlight, as a string\n    const code = `var data = 1;`;\n\n    // Returns a highlighted HTML string\n    const html = Prism.highlight(code, Prism.languages.javascript, \'javascript\');</code></pre>\n\n</body>\n</html>\n',
                'content': {
                    'html': '<tr>\n            <td rowspan="2">1</td>\n            <td>2</td>\n            <td>3</td>\n        </tr>\n        ',
                    'is_complex': 'complex',
                },
            }


if __name__ == '__main__':
    r = TestTableRecognizer()
    r.setUp()
    r.test_table_to_content_list_node_complex()
