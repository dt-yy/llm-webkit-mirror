from pydantic import BaseModel

from llm_web_kit.libs.statics import Statics


class Result(BaseModel):
    def __init__(self):
        pass


class Evaluator:
    def __init__(self):
        pass

    def eval_type_acc(self, base, pre: Statics):
        """评估类型准确率.
        base: 基础数据，pre: 预测数据; 格式：
        {
            "statics": {
                "list": 1,
                "list.text": 2,
                "list.equation-inline": 1,
                "paragraph": 2
            }
        }
        返回评估结果：
        "result_summary": { # 评测结果
            "Overall": {
                "count": 52000, # 元素数量
                "type_acc": 0.9997, # 元素类型识别准确性
                "content_acc": 0.9997 # 元素内容识别准确性
            },
            "equation-interline": {
                "count": 52, # 元素数量
                "type_acc": 0.9997, # 元素类型识别准确性
                "content_acc": 0.9997 # 元素内容识别准确性
            },
            "code": {
                "count": 5, # 元素数量
                "type_acc": 0.9997, # 元素类型识别准确性
                "content_acc": 0.9997 # 元素内容识别准确性
            },
                    ...
        }
        """
        # 计算准确率
        pass

    def eval_content_acc(self, base, pre: str):
        """评估内容准确率.

        base: 基础数据
        pre: 预测数据
        """
        pass
