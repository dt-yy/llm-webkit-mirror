import sys
import unittest
from pathlib import Path


class TestST(unittest.TestCase):
    """基于bench/data/origin目录下的数据进行抽取集成测试."""

    def setUp(self):
        """设置测试环境."""
        # 获取项目根目录的绝对路径
        root_path = Path(__file__).parent.parent.parent.absolute()
        print('rootPath: ', root_path)

        # 将项目根目录添加到Python路径
        if str(root_path) not in sys.path:
            sys.path.insert(0, str(root_path))

    def test_st_bench(self):
        """测试run.py."""
        from bench.run import main

        summary, detail = main()
        self.assertIsNotNone(summary)
        self.assertIsNotNone(detail)
        self.assertEqual(summary.error_summary['count'], 0, msg=f'测试数据抽取有失败, 抽取失败的数据详情参考: {detail.to_dict()}')


if __name__ == '__main__':
    r = TestST()
    r.setUp()
    r.test_st_bench()
