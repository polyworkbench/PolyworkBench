<div align="center">
<img src="polyworkbench.png" width="160" alt="PolyWorkBench Logo">

<h1 align="center">PolyWorkBench</h1>

<p align="center">
  <strong>跨语言长程 Agent 评测基准</strong>
</p>

<p align="center">
  <em>67 个多语种任务 | 10 种语言 | 5 大领域 | 基于 Ground Truth 的精确评分</em>
</p>

<p align="center">
  <a href="#排行榜"><img alt="Tasks" src="https://img.shields.io/badge/tasks-67-blue"></a>
  <a href="#排行榜"><img alt="Languages" src="https://img.shields.io/badge/languages-10-green"></a>
  <a href="#排行榜"><img alt="Domains" src="https://img.shields.io/badge/domains-5-purple"></a>
  <a href="#排行榜"><img alt="Models" src="https://img.shields.io/badge/models-5+-orange"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-yellow"></a>
  <a href="https://polyworkbench.github.io/"><img alt="Leaderboard" src="https://img.shields.io/badge/🏆_Leaderboard-PolyWorkBench-8c2416"></a>
</p>

> English version: [README.md](README.md)
</div>

---

## 目录

- [为什么需要 PolyWorkBench？](#为什么需要-polyworkbench)
- [排行榜](#排行榜)
- [任务总览](#任务总览)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [任务结构](#任务结构)
- [支持的 Harness](#支持的-harness)
- [脚本与工具](#脚本与工具)
- [添加自定义任务](#添加自定义任务)
- [常见问题](#常见问题)
- [引用](#引用)
- [许可证](#许可证)

---

> **跨语言、长程的 Agent 真实工作场景评测。** PolyWorkBench 把 AI Agent 投放到大量多语言文档的真实工作场景中——解析日文票据、审计德文合同、把韩文告警日志和中文传感器数据做时间相关分析——衡量它们能否跨越语言障碍交付**正确且可验证**的结果。
>
> **三轨评分。** 每个任务由 pytest 结构化测试、加权多维 `grade()` 和 LLM-as-Judge 质量评估三套独立机制打分。

---

## 为什么需要 PolyWorkBench？

大多数 Agent 基准只测试单语言、单步能力。但真实的企业工作不是这样：

|  | 我们考察什么 | 难点在哪里 |
|:---:|---|---|
| **跨语言** | 同时处理 3-5 种语言的来源材料 | 不只是翻译，而是从中文 CSV、韩文告警、俄文日志中**抽取并计算** |
| **长程** | 多步骤、上下游依赖的流水线 | 第 N 步的产物喂入第 N+1 步，无法跳过或抄近路 |
| **精确验证** | 基于 Ground Truth 的数值断言 | 不是"看起来对不对"，而是"总额是不是恰好 47,250" |
| **领域多样** | 商业、法律、制造、知识、本地化 | 每个领域都有自己的多语言挑战 |

### 核心特性

- **10 种语言、真实内容。** 非机器翻译——使用具有领域术语的母语原始文档（日文 軽減税率、韩文 적합/부적합、德文 Rahmenvertrag）。
- **三轨评分。** 每个任务由三套独立机制打分：(1) pytest 结构化测试；(2) 带 Ground Truth 断言的加权多维 `grade()`；(3) LLM-as-Judge 质量评估。
- **预埋 Ground Truth。** 输入文件中包含可精确校验的事实（金额、日期、ID），评分脚本逐项核对。
- **Harness 无关。** 同一批任务可在 OpenClaw、Claude Code、Codex CLI 或任意通过 Docker 接入的 Agent 框架上运行。
- **隔离可复现。** 每个任务在独立 Docker 容器内运行，输入文件按需注入；评分脚本对 Agent 不可见。

---

## 排行榜

完整交互式排行榜：[polyworkbench.github.io](https://polyworkbench.github.io/)

> 所有分数为 **n=1**（单次运行），基于完整 67 任务套件（v4）。Pass@3 / Pass^3 鲁棒性评测即将发布。

| 排名 | 模型 | 机构 | 平均 Grade | COM | KNW | LEG | LOC | MFG | 任务数 |
|:----:|------|------|:---------:|:---:|:---:|:---:|:---:|:---:|:-----:|
| 🥇 | **Minimax-M2.7** | MiniMax | 0.729 | 0.779 | 0.691 | 0.623 | 0.752 | 0.797 | 67 |
| 🥈 | **Minimax-M3** | MiniMax | 0.724 | 0.703 | 0.745 | 0.646 | 0.681 | 0.847 | 67 |
| 🥉 | **Claude Opus 4.8** | Anthropic | 0.712 | 0.661 | 0.751 | 0.618 | 0.750 | 0.808 | 67 |
| 4 | **Qwen3.6-27B** | Alibaba Cloud | 0.659 | 0.584 | 0.536 | 0.662 | 0.770 | 0.750 | 67 |
| 5 | **Qwen3.6-35B-A3B** | Alibaba Cloud | 0.650 | 0.464 | 0.684 | 0.650 | 0.696 | 0.800 | 67 |
| 6 | **DeepSeek-v4-Flash** | DeepSeek | 0.475 | 0.386 | 0.432 | 0.565 | 0.551 | 0.452 | 67 |

---

## 任务总览

67 个任务横跨 5 个领域，难度 L3-L6，覆盖 10 种指令/原文语言。

### 领域分布

| 领域 | 任务数 | 描述 | 示例 |
|------|:-----:|------|------|
| **COM**（商业） | 16 | 跨境贸易、定价、欺诈、合规 | 多币种对账，识别 3 处预埋差异 |
| **KNW**（知识） | 11 | 研究综合、事实核查、矛盾检测 | 跨语言事实核查，需用到全部 4 种语言来源 |
| **LEG**（法律） | 15 | 合同审查、证据链、专利分析 | 德文合同冲突检测（6 处预埋条款冲突） |
| **LOC**（本地化） | 11 | 应用文案、游戏台词、代码文档、UI 一致性 | 跨平台 UI 文案不一致检测（8 处预埋） |
| **MFG**（制造） | 14 | SRE 根因、质量分析、交接班 | 跨韩/中/英日志做时间戳关联以定位根因 |

### 语言覆盖

| 语言 | 任务数 | 角色 |
|------|:-----:|------|
| 韩语 (ko) | 12 | 指令 + 原文 |
| 英语 (en) | 12 | 指令 + 原文 |
| 法语 (fr) | 8 | 指令 + 原文 |
| 俄语 (ru) | 8 | 原文 |
| 日语 (ja) | 7 | 指令 + 原文 |
| 越南语 (vi) | 7 | 指令 + 原文 |
| 中文 (zh) | 7 | 指令 + 原文 |
| 西班牙语 (es) | 4 | 指令 + 原文 |
| 德语 (de) | 3 | 指令 + 原文 |
| 阿拉伯语 (ar) | 1 | 指令（RTL） |

### 难度分布

| 难度 | 任务数 | 平均 grade（M2.7） | 描述 |
|:----:|:-----:|:-----------------:|------|
| L3 | 8 | 0.75 | 基线：2-3 个原文文件，结构化输出 |
| L4 | 26 | 0.82 | 多源交叉引用，需要精确计算 |
| L5 | 23 | 0.65 | 深度流水线：4+ 来源，迭代验证 |
| L6 | 10 | 0.45 | 压力档：5+ 语言，异常检测，决策树 |

---

## 快速开始

### 环境要求

- Python 3.9+
- Docker（用于容器化 Agent 执行）
- 目标模型的 API Key（支持 OpenRouter、Anthropic、DeepSeek、MiniMax 等）

### 1. 安装

```bash
git clone https://github.com/polyworkbench/PolyWorkBench.git
cd PolyWorkBench
pip install -r src/agent/requirements.txt
```

### 2. 下载并加载 Docker 镜像

镜像托管在 HuggingFace 上。下载你需要的 Harness 镜像：

```bash
pip install -U "huggingface_hub[cli]"

# 下载 OpenClaw 镜像（推荐首次使用）
huggingface-cli download polyworkbench/PolyWorkBench \
    Images/polyworkbench-openclaw.tar \
    --repo-type dataset --local-dir .

# 加载到 Docker
docker load -i Images/polyworkbench-openclaw.tar
```

> 完整镜像列表见 [支持的 Harness](#支持的-harness) 章节。

### 3. 配置 API Key

```bash
cp src/agent/.env.example src/agent/.env
```

编辑 `src/agent/.env`，选择以下任一配置：

**方案 A：OpenRouter（推荐，支持多模型切换）**
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514
```

**方案 B：Anthropic 直连**
```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
ANTHROPIC_BASE_URL=https://api.anthropic.com
DEFAULT_MODEL=claude-sonnet-4-20250514
```

**方案 C：DeepSeek**
```env
OPENROUTER_API_KEY=sk-xxxxxxxxxxxx
OPENROUTER_BASE_URL=https://api.deepseek.com
DEFAULT_MODEL=deepseek-chat
```

**方案 D：MiniMax**
```env
OPENROUTER_API_KEY=sk-xxxxxxxxxxxx
OPENROUTER_BASE_URL=https://api.minimaxi.com/v1
DEFAULT_MODEL=minimax/MiniMax-M2.7
```

LLM Judge 模型配置（可选，默认使用相同 Key）：
```env
JUDGE_API_KEY=sk-ant-xxxxxxxxxxxx
JUDGE_BASE_URL=https://api.anthropic.com
JUDGE_MODEL=claude-sonnet-4-20250514
```

### 4. 一键运行（验证安装）

```bash
bash run.sh
```

该脚本会自动检查环境、安装依赖，并运行一个演示任务。

### 5. 运行单个任务

```bash
python3 -m src.agent \
    --task COM-09_ko_compliance_check \
    --harness openclaw \
    --model "your-model-name" \
    --tasks-dir full_tasks \
    --grade-on-error
```

### 6. 批量运行

```bash
python3 -m src.agent \
    --all \
    --harness openclaw \
    --model "your-model-name" \
    --tasks-dir full_tasks \
    --output-dir output/ \
    --grade-on-error \
    --parallel 3
```

常用筛选参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `--collection` | 按集合筛选 | `--collection smoke` |
| `--max-difficulty` | 仅跑难度 <= N 的任务 | `--max-difficulty 4` |
| `--tags` | 仅跑同时带这些 tag 的任务 | `--tags ko-instruction zh-source` |
| `--parallel` | 并行任务数 | `--parallel 5` |

### 7. 查看结果

每个任务的产物位于 `output/<harness>/<task_id>/<model>_<timestamp>_<run_id>/`：

- `result.json` — `overall_score`、各维度分、错误信息、Token/费用统计
- `agent.log` / `gateway.log` — Agent 与网关的执行日志
- `task_output/` — Agent 在容器中生成的全部输出

结果示例：
```json
{
  "task_id": "COM-09_ko_compliance_check",
  "scores": {
    "overall_score": 0.82,
    "pytest_score": 1.0,
    "judge_score": 0.72,
    "dimensions": {"structure": 0.9, "accuracy": 0.8, "coverage": 0.75}
  },
  "usage": {
    "input_tokens": 5234,
    "output_tokens": 1823,
    "cost_usd": 0.0234,
    "elapsed_time": 45.2
  }
}
```

---

## 项目结构

```
PolyWorkBench/
├── run.sh                       # 一键运行入口
├── scripts/
│   ├── run_smoke.sh             # 冒烟测试（少量任务，快速验证）
│   └── run_full_eval.sh         # 全量评测（67 任务 x 3 轮）
├── config/
│   └── task.example.toml        # 任务配置模板（带注释）
├── full_tasks/                  # 全部 67 个评测任务
│   ├── COM-00_ja_receipt.../
│   ├── COM-01_ru_marketplace.../
│   ├── KNW-02_ko_tech.../
│   ├── LEG-00_es_privacy.../
│   ├── LOC-01_ko_game.../
│   └── MFG-01_ko_sre.../
├── src/
│   └── agent/                   # 评测框架代码
│       ├── __main__.py          # 入口: python -m src.agent
│       ├── run_batch.py         # 主编排器
│       ├── run_full_eval.py     # 全量评测（Pass@3 指标）
│       ├── run_judge_rescore.py # 对已有输出重跑 LLM Judge
│       ├── harness_registry.py  # Harness -> Docker 镜像映射
│       ├── base.py              # BaseAgent 接口定义
│       ├── .env.example         # 环境变量模板
│       ├── requirements.txt     # Python 依赖
│       ├── agents/              # 各 Harness Runner 实现
│       │   ├── openclaw/
│       │   ├── claudecode/
│       │   ├── codex/
│       │   └── hermesagent/
│       └── utils/               # 共享工具
│           ├── cli_args.py      # CLI 参数解析
│           ├── docker_utils.py  # 容器管理
│           ├── grading.py       # 三轨评分
│           ├── judge.py         # LLM-as-Judge 实现
│           └── task_parser.py   # task.toml + instruction.md 解析
├── output/                      # 评测结果（不入库）
├── CONTRIBUTING.md              # 贡献指南
├── LICENSE                      # Apache 2.0
├── README.md                    # 英文文档
└── README.zh-CN.md              # 本文件
```

---

## 任务结构

每个任务是一个自包含目录：

```
full_tasks/COM-09_ko_compliance_check/
├── task.toml              # 元数据：id、难度、超时、tag
├── instruction.md         # 任务指令（目标语言）
├── environment/
│   ├── Dockerfile         # 容器环境定义
│   └── inputs/            # 多语言原文输入（只读挂载）
│       ├── fda_requirements_en.json
│       ├── gb_standards_zh.txt
│       └── jis_standards_ja.txt
└── tests/
    ├── test.sh            # 评分入口
    ├── test_outputs.py    # grade() + pytest 断言
    ├── expected_output_schema.json  # 输出 JSON Schema
    └── rubric.md          # LLM Judge 维度定义
```

### 评分架构

```
+---------------------------------------------------------+
|  Track 1：pytest      -> pass/fail（结构性闸门）          |
|  Track 2：grade()     -> 0-1.0 加权多维评分               |
|  Track 3：LLM Judge   -> 0-1.0 质量评估                   |
+---------------------------------------------------------+
主指标：grade()（Track 2）
- 各维度加权 + 非线性缩放
- Ground Truth 数值断言权重 x2
- 全部通过封顶 0.85；1.0 仅留给完美匹配 Ground Truth 的产出
```

---

## 支持的 Harness

PolyWorkBench 提供 **四个** Docker 镜像，每个 Harness 一个。镜像托管在 [HuggingFace](https://huggingface.co/datasets/polyworkbench/PolyWorkBench)。

| Harness | 镜像文件 | 加载后的 Tag |
|---------|---------|-------------|
| **openclaw** | `polyworkbench-openclaw.tar` | `polyworkbench-openclaw:v1` |
| **claudecode** | `polyworkbench-claudecode.tar` | `polyworkbench-claudecode:v1` |
| **codex** | `polyworkbench-codex.tar` | `polyworkbench-codex:v1` |
| **hermesagent** | `polyworkbench-hermes.tar` | `polyworkbench-hermes:v1` |

### 下载与加载镜像

```bash
pip install -U "huggingface_hub[cli]"

# 下载所需镜像（可选择性下载，或全部下载）
huggingface-cli download polyworkbench/PolyWorkBench \
    Images/polyworkbench-openclaw.tar \
    Images/polyworkbench-claudecode.tar \
    Images/polyworkbench-codex.tar \
    Images/polyworkbench-hermes.tar \
    --repo-type dataset --local-dir .

# 加载到 Docker
docker load -i Images/polyworkbench-openclaw.tar
docker load -i Images/polyworkbench-claudecode.tar
docker load -i Images/polyworkbench-codex.tar
docker load -i Images/polyworkbench-hermes.tar
```

### 覆盖镜像

如需使用自定义镜像（如本地构建或私有仓库），可通过环境变量覆盖：

```bash
# 按 Harness 单独覆盖
export LONGHORIZON_OPENCLAW_IMAGE=my-registry/custom-openclaw:v2
export LONGHORIZON_CLAUDECODE_IMAGE=my-registry/custom-claudecode:v2
export LONGHORIZON_CODEX_IMAGE=my-registry/custom-codex:v2
export LONGHORIZON_HERMES_IMAGE=my-registry/custom-hermes:v2

# 全局覆盖（对所有 Harness 生效）
export LONGHORIZON_DOCKER_IMAGE=my-universal-image:latest
```

或通过 CLI 参数：
```bash
python3 -m src.agent --task ... --image my-registry/custom:v2
```

---

## 脚本与工具

### `run.sh` — 一键入口

```bash
bash run.sh                                    # 运行演示任务
bash run.sh --task COM-09_ko_compliance_check  # 指定任务
bash run.sh --all --parallel 3                 # 全部任务
bash run.sh --collection smoke                 # 冒烟测试
```

### `scripts/run_smoke.sh` — 冒烟测试

快速验证安装是否正常：
```bash
bash scripts/run_smoke.sh
bash scripts/run_smoke.sh --harness claudecode
PARALLEL=4 bash scripts/run_smoke.sh
```

### `scripts/run_full_eval.sh` — 全量评测

运行全部 67 任务 x 3 轮，产出 Pass@3 / Pass^3 统计指标：
```bash
bash scripts/run_full_eval.sh
```

### 完整 CLI 参数列表

```
--task TASK_ID                        运行指定任务
--all                                 运行全部任务
--collection {smoke|baseline|stress}  按集合筛选

--harness {openclaw|claudecode|codex|hermesagent}  选择 Harness
--model MODEL_NAME                    使用的模型
--parallel N                          并行任务数

--max-difficulty N                    仅跑难度 <= N 的任务
--tags TAG1 TAG2                      任务必须包含所有指定 tag

--skip-grading                        跳过评分（调试模式）
--grade-on-error                      即使 Agent 报错也评分
--timeout-override SECONDS            覆盖任务超时时间

--tasks-dir PATH                      任务目录
--output-dir PATH                     结果目录
--image DOCKER_IMAGE                  覆盖 Docker 镜像
```

---

## 添加自定义任务

1. 在 `full_tasks/` 下按命名规则建目录：`{DOMAIN}-{NUM}_{lang}_{description}`
2. 编写 `task.toml`（参考 [`config/task.example.toml`](config/task.example.toml)）
3. 用目标语言编写 `instruction.md`
4. 把多语言原文放入 `environment/inputs/`
5. 在 `tests/test_outputs.py` 中实现 `grade()` 与 pytest 断言
6. 在 `tests/rubric.md` 中定义 LLM Judge 评分维度

详细规范见 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 常见问题

### Docker 守护进程未运行
确保 Docker Desktop 已启动：
```bash
# Linux
sudo systemctl start docker

# macOS
open -a Docker
```

### 镜像未找到
重新下载并加载镜像：
```bash
huggingface-cli download polyworkbench/PolyWorkBench \
    Images/polyworkbench-openclaw.tar \
    --repo-type dataset --local-dir .
docker load -i Images/polyworkbench-openclaw.tar

# 或在 .env 中设置：
# LONGHORIZON_OPENCLAW_IMAGE=your-registry/your-image:tag
```

### API Key 未设置
编辑 `src/agent/.env`，参见上方[配置 API Key](#2-配置-api-key)。

### "Connection refused" / 代理问题
取消代理环境变量：
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
python3 -m src.agent --task ...
```

### 任务超时
覆盖超时时间：
```bash
python3 -m src.agent --task ... --timeout-override 3600
```

### "No tasks found"
检查 `--tasks-dir` 是否指向正确目录：
```bash
python3 -m src.agent --task COM-09_ko_compliance_check --tasks-dir full_tasks
```

---

## 引用

```bibtex
@misc{polyworkbench2026,
  title={PolyWorkBench: A Cross-Lingual Long-Horizon Agent Benchmark},
  author={PolyWorkBench Team},
  year={2026},
  url={https://github.com/polyworkbench/PolyWorkBench}
}
```

---

## 许可证

本项目采用 Apache License 2.0 协议——详见 [LICENSE](LICENSE)。

任务内容（指令、输入）可能包含来自公共领域或 CC 协议来源的节选，具体出处见各任务 `task.toml` 文件中的标注。

---

## 贡献

欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细指南。

---

<p align="center">
  <em>PolyWorkBench — 在语言与工作交汇处评测 Agent。</em>
</p>
