

from abc import ABC, abstractmethod
from llm_web_kit.input.datajson import ContentList, DataJson
from overrides import override


class AbstractPipeline(ABC):
    """抽象的pipeline类，定义了pipeline的接口规范

    Args:
        ABC (_type_): _description_

    Raises:
        NotImplementedError: _description_
        NotImplementedError: _description_
    """
    @abstractmethod
    def format(self, data:DataJson) -> DataJson:
        raise NotImplementedError

    @abstractmethod
    def extract(self, dict) -> DataJson:
        raise NotImplementedError
    

class Pipeline(AbstractPipeline):
    """实现每个数据集一个pipeline的设计模式
    所有的pipeline构成一个优先级处理链
    format() ---> extract() ---> other...

    """
    def __init__(self, config: dict):
        self.__validate(config)
        self.__config = config

        self.__formator = None
        self.__extractor = None

    @override
    def format(self, data:DataJson) -> DataJson:
        pass

    @override
    def extract(self, dict) -> DataJson:
        pass

    def __validate(self, config: dict):
        """校验一下配置里必须满足的条件，否则抛出异常

        Args:
            config (dict): _description_
        """
        pass
