# VulnSeek

一个使用 Python 标准库的单 Agent 项目。CLI 负责装配依赖，运行时负责推进对话和分发工具调用。

## 快速开始

在仓库根目录使用 Python 3.9 或以上版本运行离线演示。

```sh
python3 -m agent_workbench --demo "hello from the agent"
```

预期输出为 `Word count: 4`。演示使用固定的模型适配器，完整经过工具调用和结果回传。

使用支持 Chat Completions 工具调用的模型时，在环境中设置 `AGENT_BASE_URL`、`AGENT_MODEL` 和 `AGENT_API_KEY`。基础 URL 包含服务的 API 前缀，程序会追加 `/chat/completions`。随后运行：

```sh
python3 -m agent_workbench "请用工具统计 hello from the agent 的词数"
```

## 模块

| 模块 | 职责 |
| --- | --- |
| `__main__.py` | 解析命令行参数，选择模型和注册工具 |
| `runtime.py` | 管理本次对话，执行工具调用并回传结果，限制模型轮次和单轮调用次数 |
| `models.py` | 实现离线演示和 HTTP 模型适配 |
| `tools.py` | 定义工具声明和参数校验，提供只读的词数统计 |

每次执行建立一段内存中的对话。调用 HTTP 模型时，当前对话和工具结果会发送给配置的模型服务。
