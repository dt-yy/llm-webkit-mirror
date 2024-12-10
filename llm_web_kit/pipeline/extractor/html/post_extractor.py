from overrides import override

from llm_web_kit.input.datajson import DataJson
from llm_web_kit.pipeline.extractor.post_extractor import \
    BaseFileFormatPostExtractor


class HTMLFileFormatPostExtractor(BaseFileFormatPostExtractor):
    """一个从html文件中提取数据的提取器.

    Args:
        BaseFileFormatPostExtractor (_type_): 一个基础的规则过滤提取器
    """

    @override
    def _filter_by_rule(self, data_json: DataJson) -> bool:
        """根据规则过滤content_list.

        Args:
            data_json (DataJson): 判断content_list是否是自己想要拦截处理的数据

        Returns:
            bool: 如果是希望处理的数据，返回True，否则返回False
        """
        return self.is_html_format(data_json)

    @override
    def _do_post_extract(self, data_json: DataJson) -> DataJson:
        """实现真正的数据提取.

        Args:
            data_json (DataJson): 需要处理的数据集
        """
        # TODO
        raise NotImplementedError('Subclass must implement abstract method')
