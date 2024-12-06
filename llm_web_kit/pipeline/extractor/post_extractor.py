

from abc import ABC, abstractmethod
from overrides import override
from llm_web_kit.input.datajson import ContentList
from llm_web_kit.pipeline.extractor.base import FileTypeMatcher


class AbstractPostExtractor(ABC):
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

    def post_extract(self, content_list: ContentList) -> ContentList:
        """实现针对一条输入数据的提取

        Args:
            content_list (ContentList): _description_

        Returns:
            dict: _description_
        """
        if self._filter_by_rule(content_list):
            return self._do_post_extract(content_list)
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
    def _do_post_extract(self, content_list:ContentList) -> ContentList:
        """实现真正的数据提取

        Args:
            content_list (ContentList): 需要处理的数据集
        """
        raise NotImplementedError("Subclass must implement abstract method")
    

class BaseRuleFilterPostExtractor(AbstractPostExtractor):
    """一个基础的规则过滤提取器

    Args:
        AbstractPostExtractor (_type_): 一个抽象的数据提取器
    """
    pass
    

class BaseFileFormatPostExtractor(BaseRuleFilterPostExtractor, FileTypeMatcher):
    """一个基础的规则过滤提取器

    Args:
        AbstractPostExtractor (_type_): 一个抽象的数据提取器
    """
    pass
    

class HTMLPostExtractor(BaseFileFormatPostExtractor):
    """一个从html文件中提取数据的提取器

    Args:
        BaseFileFormatPostExtractor (_type_): 一个基础的规则过滤提取器
    """
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
    def _do_post_extract(self, content_list:ContentList) -> ContentList:
        """实现真正的数据提取

        Args:
            content_list (ContentList): 需要处理的数据集
        """
        # TODO 
        raise NotImplementedError("Subclass must implement abstract method")
    

class MDPostExtractor(BaseFileFormatPostExtractor):
    """一个从MD文件中提取数据的提取器

    Args:
        BaseFileFormatPostExtractor (_type_): 一个基础的规则过滤提取器
    """
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
    def _do_post_extract(self, content_list:ContentList) -> ContentList:
        """实现真正的数据提取

        Args:
            content_list (ContentList): 需要处理的数据集
        """
        # TODO 
        raise NotImplementedError("Subclass must implement abstract method")
    

class TXTPostExtractor(BaseFileFormatPostExtractor):
    """一个从TXT文件中提取数据的提取器

    Args:
        BaseFileFormatPostExtractor (_type_): 一个基础的规则过滤提取器
    """
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
    def _do_post_extract(self, content_list:ContentList) -> ContentList:
        """实现真正的数据提取

        Args:
            content_list (ContentList): 需要处理的数据集
        """
        # TODO 
        raise NotImplementedError("Subclass must implement abstract method")
    

class PDFPostExtractor(BaseFileFormatPostExtractor):
    """一个从PDF文件中提取数据的提取器

    Args:
        BaseFileFormatPostExtractor (_type_): 一个基础的规则过滤提取器
    """
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
    def _do_post_extract(self, content_list:ContentList) -> ContentList:
        """实现真正的数据提取

        Args:
            content_list (ContentList): 需要处理的数据集
        """
        # TODO 
        raise NotImplementedError("Subclass must implement abstract method")
<<<<<<< HEAD
    
class NoOpPostExtractor(BaseRuleFilterPostExtractor):
    """一个什么都不做的提取器

    Args:
        BaseRuleFilterPostExtractor (_type_): 一个基础的规则过滤提取器
    """
    @override
    def _filter_by_rule(self, content_list:ContentList) -> bool:
        """根据规则过滤content_list

        Args:
            content_list (ContentList): 判断content_list是否是自己想要拦截处理的数据

        Returns:
            bool: 如果是希望处理的数据，返回True，否则返回False
        """
        return True
    
    @override
    def _do_post_extract(self, content_list:ContentList) -> ContentList:
        """实现真正的数据提取

        Args:
            content_list (ContentList): 需要处理的数据集
        """
        return content_list
=======
    
>>>>>>> a283f237251e02da623fa15fa3cd49f9184ee505
