from abc import ABC, abstractmethod
from overrides import override
from llm_web_kit.input.datajson import ContentList
from llm_web_kit.pipeline.extractor.base import FileTypeMatcher


class AbstractExtractor(ABC):
    """一个抽象的数据提取器

    Args:
        ABC (_type_): _description_
    """
    
    def __init__(self, config: dict):
        """从参数指定的配置中初始化这个流水线链

        Args:
            config (dict): 配置字典
        """
        self.__config = config


    def extract(self, content_list: ContentList) -> ContentList:
        """实现针对一条输入数据的提取

        Args:
            content_list (ContentList): _description_

        Returns:
            dict: _description_
        """
        if self._filter_by_rule(content_list):
            return self._do_extract(content_list)
        else:
            return content_list
    

    @abstractmethod
    def _filter_by_rule(self, content_list:ContentList) -> bool:
        """根据规则过滤content_list

        Args:
            content_list (ContentList): 判断content_list是否是自己想要拦截处理的数据

        Returns:
            bool: 如果是希望处理的数据，返回True，否则返回False
        """
        raise NotImplementedError("Subclass must implement abstract method")
    
    @abstractmethod
    def _do_extract(self, content_list:ContentList) -> ContentList:
        """实现真正的数据提取

        Args:
            content_list (ContentList): 需要处理的数据集
        """
        raise NotImplementedError("Subclass must implement abstract method")
    

    
class BaseRuleFilterExtractor(AbstractExtractor):
    """一个从markdown文件中提取数据的提取器

    Args:
        AbstractExtractor (_type_): _description_
    """
    
    def __init__(self, config: dict):
        """从参数指定的配置中初始化这个流水线链

        Args:
            config (dict): 配置字典
        """
        super().__init__(config)
    

class BaseFileFormatExtractor(BaseRuleFilterExtractor, FileTypeMatcher):
    """一个从html文件中提取数据的提取器

    Args:
        AbstractExtractor (_type_): _description_
    """
    
    def __init__(self, config: dict):
        """从参数指定的配置中初始化这个流水线链

        Args:
            config (dict): 配置字典
        """
        super().__init__(config)


class MDFileExtractor(BaseFileFormatExtractor):
    """一个从markdown文件中提取数据的提取器

    Args:
        BaseFileFormatExtractor (_type_): _description_
    """
    
    def __init__(self, config: dict):
        """从参数指定的配置中初始化这个流水线链

        Args:
            config (dict): 配置字典
        """
        super().__init__(config)

    @override
    def _filter_by_rule(self, content_list:ContentList) -> bool:
        """根据规则过滤content_list

        Args:
            content_list (ContentList): 判断content_list是否是自己想要拦截处理的数据

        Returns:
            bool: 如果是希望处理的数据，返回True，否则返回False
        """
        return self.is_md_format(content_list)
    
    @override
    def _do_extract(self, content_list:ContentList) -> ContentList:
        """实现真正的数据提取

        Args:
            content_list (ContentList): 需要处理的数据集
        """
        # TODO
        raise NotImplementedError("Subclass must implement abstract method")
    

class TXTFileExtractor(BaseFileFormatExtractor):
    """一个从txt文件中提取数据的提取器

    Args:
        BaseFileFormatExtractor (_type_): _description_
    """
    
    def __init__(self, config: dict):
        """从参数指定的配置中初始化这个流水线链

        Args:
            config (dict): 配置字典
        """
        super().__init__(config)

    @override
    def _filter_by_rule(self, content_list:ContentList) -> bool:
        """根据规则过滤content_list

        Args:
            content_list (ContentList): 判断content_list是否是自己想要拦截处理的数据

        Returns:
            bool: 如果是希望处理的数据，返回True，否则返回False
        """
        return self.is_txt_format(content_list)
    
    @override
    def _do_extract(self, content_list:ContentList) -> ContentList:
        """实现真正的数据提取

        Args:
            content_list (ContentList): 需要处理的数据集
        """
        # TODO
        raise NotImplementedError("Subclass must implement abstract method")
    

class HTMLFileExtractor(BaseFileFormatExtractor):
    """一个从html文件中提取数据的提取器

    Args:
        BaseFileFormatExtractor (_type_): _description_
    """
    
    def __init__(self, config: dict):
        """从参数指定的配置中初始化这个流水线链

        Args:
            config (dict): 配置字典
        """
        super().__init__(config)

    @override
    def _filter_by_rule(self, content_list:ContentList) -> bool:
        """根据规则过滤content_list

        Args:
            content_list (ContentList): 判断content_list是否是自己想要拦截处理的数据

        Returns:
            bool: 如果是希望处理的数据，返回True，否则返回False
        """
        return self.is_html_format(content_list)
    
    @override
    def _do_extract(self, content_list:ContentList) -> ContentList:
        """实现真正的数据提取

        Args:
            content_list (ContentList): 需要处理的数据集
        """
        # TODO
        raise NotImplementedError("Subclass must implement abstract method")
    

class PDFFileExtractor(BaseFileFormatExtractor):
    """一个从pdf文件中提取数据的提取器

    Args:
        BaseFileFormatExtractor (_type_): _description_
    """
    
    def __init__(self, config: dict):
        """从参数指定的配置中初始化这个流水线链

        Args:
            config (dict): 配置字典
        """
        super().__init__(config)

    @override
    def _filter_by_rule(self, content_list:ContentList) -> bool:
        """根据规则过滤content_list

        Args:
            content_list (ContentList): 判断content_list是否是自己想要拦截处理的数据

        Returns:
            bool: 如果是希望处理的数据，返回True，否则返回False
        """
        return self.is_pdf_format(content_list)
    
    @override
    def _do_extract(self, content_list:ContentList) -> ContentList:
        """实现真正的数据提取

        Args:
            content_list (ContentList): 需要处理的数据集
        """
        # TODO
        raise NotImplementedError("Subclass must implement abstract method")
