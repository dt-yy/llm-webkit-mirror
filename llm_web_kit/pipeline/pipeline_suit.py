import commentjson as json
from overrides import override

from llm_web_kit.exception.exception import PipelineInitExp
from llm_web_kit.input.datajson import ContentList, DataJson, DataJsonKey
from llm_web_kit.pipeline.pipeline import Pipeline


class PipelineSuit(object):
    """实现数据集处理pipeline的按需实例化，并调用方法的设计模式
    从数据源到数据集的处理链
    例如，从文件到contentList的处理链

    """
    def __init__(self, config_file_path: str):
        """从参数指定的配置文件中读取配置并初始化这个流水线链

        Args:
            config_file_path (str): 配置文件的路径
        """
        with open(config_file_path, 'r', encoding='utf-8') as file:
            self.__config = json.load(file)
            self.__init__(self.__config)

    def __init__(self, config: dict):
        """从参数指定的配置中初始化这个流水线链

        Args:
            config (dict): 配置字典
        """
        self.__config = config # 先不初始化那么多实例，用到哪个实例再初始化
        self.__pipelines = {} # "dataset_name" => pipeline


    def __getattr__(self, method_name):
        """ 动态转发方法到具体和dataset_name绑定的pipeline实例上
        例如：
        pipsuit = PipelineSuit("/path/to/datasource_config.jsonc")
        pipsuit.extract({"dataset_name": "zlib"}) # 此时会调用zlib的pipeline实例的extract方法

        Args:
            method_name (_type_): _description_

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            AttributeError: _description_

        Returns:
            _type_: _description_
        """
        # 这个方法会在访问的属性在PipelineSuit中不存在时被调用
        def method(*args, **kwargs):
            if not args:
                raise PipelineInitExp(f"First argument must be the JSON object containing 'dataset_name'.")

            json_obj = args[0]
            if not isinstance(json_obj, dict) or 'dataset_name' not in json_obj:
                raise PipelineInitExp("JSON object must be a dictionary containing 'dataset_name'.")

            dataset_name = json_obj[DataJsonKey.DATASET_NAME]
            pipeline = self.__pipelines.get(dataset_name)
            
            if not pipeline:
                try:
                    pipeline_config = self.__config[dataset_name]
                    pipeline_of_dataset = Pipeline(pipeline_config)
                    self.__pipelines[dataset_name] = pipeline_of_dataset
                except KeyError:
                    raise PipelineInitExp(f"Dataset name {dataset_name} is not found in the configuration file.")
                except Exception as e:
                    raise PipelineInitExp(f"Failed to initialize pipeline for dataset: {dataset_name}") from e

            # 检查Pipeline实例是否有这个方法
            if not hasattr(pipeline, method_name):
                raise PipelineInitExp(f"The method {method_name} is not defined in the pipeline for dataset: {dataset_name}")

            # 调用Pipeline实例的方法
            return getattr(pipeline, method_name)(*args, **kwargs)

        return method
