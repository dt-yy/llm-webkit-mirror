## 作用
负责读取配置文件的统一入口。

## 配置文件的位置和格式如下：
<b>一、位置</b>
首先读取环境变量 LLM_WEB_KIT_CFG_PATH, 如果有（注意如果环境变量有设置，但是文件不存在会报错）并且配置文件存在则读取这个配置文件。
如果环境变量不存在，则默认去用户的HOME目录下寻找名字为llm-web-kit.jsonc的配置文件

<b>二、格式</b>
配置文件的格式：
```json
{
    "s3": {
        "bucket-name":["AK", "SK", "endpoint", "addressing_style=path|virtual|auto"],
        "bucket-2": []
    },
    "xx-passwd": {
        "xxxx.zip": {"passwd": "1234", "user": "xxx"}

    },
    "logger": [
                {
                    "to": "sys.stdout",
                    "log-level": "DEBUG",
                    "log-format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
                },
                {
                    "to": "/tmp/logs/test-{time:YYYY-MM-DD}.log",
                    "rotation": "1 day",
                    "retention": "10 days",
                    "log-level": "INFO",
                    "log-format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
                },
                {
                    "to": "/tmp/logs/error-{time:YYYY-MM-DD}.log",
                    "rotation": "1 day",
                    "retention": "10 days",
                    "log-level": "ERROR",
                    "log-format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
                }
            ]
}


```

    