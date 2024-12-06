

from llm_web_kit.input.datajson import DataJson
from llm_web_kit.pipeline.formatter.base import AbstractFormatter


class HTMLFormatter(AbstractFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, data:DataJson) -> DataJson:
        return data
    


