import inspect
from pathlib import Path

import commentjson as json


class ErrorMsg:
    # 类属性，用于存储错误代码和消息
    _errors = {}

    @classmethod
    def _load_errors(cls):
        # 从JSON文件中加载错误代码和消息
        exception_defs_file_path = Path(__file__).parent / 'exception.jsonc'
        with open(exception_defs_file_path, 'r', encoding='utf-8') as file:
            jso = json.load(file)
            for module, module_defs in jso.items():
                for err_name, err_info in module_defs.items():
                    err_code = err_info['code']
                    cls._errors[err_code] = {'message': err_info['message'], 'module': module, 'error_name': err_name}

    @classmethod
    def get_error_message(cls, error_code: int):
        # 根据错误代码获取错误消息
        if error_code not in cls._errors:
            return f'未知错误代码{error_code}'
        return cls._errors[str(error_code)]['message']


ErrorMsg._load_errors()


class WebKitBaseException(Exception):
    """基础的Pipeline异常类，系统中任何地方抛出的异常都必须是这个异常的子类.

    Args:
        Exception (_type_): _description_
    """

    def __init__(self, err_code: int, custom_message: str = None):
        self.err_code = err_code
        self.message = ErrorMsg.get_error_message(self.err_code)
        self.custom_message = custom_message
        super().__init__(self.message)
        frame = inspect.currentframe().f_back
        self.__py_filename = frame.f_code.co_filename
        self.__py_file_line_number = frame.f_lineno

    def __str__(self):
        return f'{self.__py_filename}: {self.__py_file_line_number}#{self.err_code}#{self.message}#{self.custom_message}'


###############################################################################
#
#  Pipeline相关的异常
#
###############################################################################
class PipelineBaseExp(WebKitBaseException):
    """Pipeline初始化异常.

    Args:
        PipelineBaseException (_type_): _description_
    """

    def __init__(self, err_code: int, custom_message: str = None):
        """pipeline对象抛出的异常基类.

        Args:
            err_code (int): _description_
            custom_message (str, optional): _description_. Defaults to None.
        """
        super().__init__(err_code, custom_message)


class PipelineInitExp(PipelineBaseExp):
    """Pipeline初始化异常.

    Args:
        PipelineBaseExp (_type_): _description_
    """

    def __init__(self, custom_message: str = None):
        """pipeline初始化异常.

        Args:
            custom_message (str, optional): _description_. Defaults to None.
        """
        super().__init__(5001, custom_message)
