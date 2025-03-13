# html layout classify layout分类

## 环境

配置 .xinghe.yaml

配置 .llm_web_kit.jsonc

## 入参

layout_sample_dir: 一个本地的目录，内含多个jsonl文件，每个文件的结构如下：

| 字段      | 类型   | 描述                         | 是否必须 |
| --------- | ------ | ---------------------------- | -------- |
| layout_id | string | layout id                    | 是       |
| url       | string | 数据url                      | 是       |
| simp_html | string | html原数据经过简化处理的html | 是       |

layout_classify_dir：分类结果的保存目录。输出的jsonl文件，每个文件的结构如下：

| 字段          | 类型   | 描述                                                            | 是否必须 |
| ------------- | ------ | --------------------------------------------------------------- | -------- |
| url_list      | list   | layout id 对应的url                                             | 是       |
| layout_id     | string | layout id                                                       | 是       |
| page_type     | string | layout_id 经过分类之后的分类结果（'other', 'article', 'forum'） | 是       |
| max_pred_prod | float  | 分类模型的分类可靠度                                            | 是       |
| version       | string | 模型版本                                                        | 是       |

## 执行步骤

1. 执行server.py，启动服务，此服务提供2个接口：

- /get_file：获取待分类的文件路径，每次一个，如果队列中没有文件，则返回空
- /update_status：更新文件分类状态
- /index：一个简单的web界面，可以查看当前的分类进度

2. 执行classify.sh，此脚本会调用server.py的/get_file接口获取待分类的文件，然后进行分类，并调用server.py的/update_status接口更新文件分类状态。

3. 执行classify-spot.sh ，可以利用spot资源。
