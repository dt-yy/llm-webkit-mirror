
from llm_web_kit.input.datajson import ContentList
from llm_web_kit.input.file_format import FileFormatConstant


class FileTypeMatcher(object):
    """文件类型匹配器

    Args:
        object (_type_): _description_
    """

    def is_md_format(self, content_list: ContentList) -> bool:
        """判断文件是否是md文件

        Args:
            file_path (str): 文件路径

        Returns:
            bool: 如果是md文件返回True，否则返回False
        """
        return content_list.get_file_format().lower() in FileFormatConstant.MARKDOWN
    

    def is_txt_format(self, content_list: ContentList) -> bool:
        """判断文件是否是txt文件

        Args:
            file_path (str): 文件路径

        Returns:
            bool: 如果是txt文件返回True，否则返回False
        """
        return content_list.get_file_format().lower() in FileFormatConstant.TXT
    

    def is_pdf_format(self, content_list: ContentList) -> bool:
        """判断文件是否是pdf文件

        Args:
            file_path (str): 文件路径

        Returns:
            bool: 如果是pdf文件返回True，否则返回False
        """
        return content_list.get_file_format().lower() in FileFormatConstant.PDF
    

    def is_html_format(self, content_list: ContentList) -> bool:
        """判断文件是否是html文件

        Args:
            file_path (str): 文件路径

        Returns:
            bool: 如果是html文件返回True，否则返回False
        """
        return content_list.get_file_format().lower() in FileFormatConstant.HTML
    