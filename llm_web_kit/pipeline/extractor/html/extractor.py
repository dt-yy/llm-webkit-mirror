from overrides import override

from llm_web_kit.input.datajson import DataJson
from llm_web_kit.pipeline.extractor.extractor import BaseFileFormatExtractor


class HTMLFileFormatExtractor(BaseFileFormatExtractor):
    """一个从html文件中提取数据的提取器.

    Args:
        BaseFileFormatExtractor (_type_): _description_
    """

    def __init__(self, config: dict):
        """从参数指定的配置中初始化这个流水线链.

        Args:
            config (dict): 配置字典
        """
        super().__init__(config)

    @override
    def _filter_by_rule(self, data_json: DataJson) -> bool:
        """根据规则过滤content_list.

        Args:
            data_json (ContentList): 判断content_list是否是自己想要拦截处理的数据

        Returns:
            bool: 如果是希望处理的数据，返回True，否则返回False
        """
        return self.is_html_format(data_json)

    @override
    def _do_extract(self, data_json: DataJson) -> DataJson:
        """实现真正的数据提取.

        Args:
            data_json (ContentList): 需要处理的数据集
        """
        # TODO
        return data_json
