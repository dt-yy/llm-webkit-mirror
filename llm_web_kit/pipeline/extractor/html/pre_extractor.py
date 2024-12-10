from overrides import override

from llm_web_kit.input.datajson import DataJson
from llm_web_kit.pipeline.extractor.pre_extractor import \
    BaseFileFormatFilterPreExtractor


class HTMLFileFormatFilterPreExtractor(BaseFileFormatFilterPreExtractor):
    """实现一个基础的HTML文件格式预处理类 例如，根据文件名的后缀拦截数据并进行基础的预处理.

    Args:
        BaseFileFormatFilterPreExtractor (_type_): _description_
    """

    def __init__(self, config: dict):
        super().__init__(config)

    @override
    def _filter_by_rule(self, data_json: DataJson) -> bool:
        return self.is_html_format(data_json)

    @override
    def _do_pre_extract(self, data_json: DataJson) -> DataJson:
        pass  # TODO
        return data_json
