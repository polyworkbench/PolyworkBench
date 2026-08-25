<div align="center">
<img src="polyworkbench.png" width="160" alt="PolyWorkBench Logo">

<h1 align="center">PolyWorkBench</h1>

<p align="center">
  <strong>跨语言长程 Agent 评测基准</strong>
</p>

<p align="center">
  <em>67 个多语种任务 | 10 种语言 | 5 大领域 | 32 个模型&times;Harness 组合</em>
</p>

<p align="center">
  <a href="#排行榜"><img alt="Tasks" src="https://img.shields.io/badge/tasks-67-blue"></a>
  <a href="#排行榜"><img alt="Languages" src="https://img.shields.io/badge/languages-10-green"></a>
  <a href="#排行榜"><img alt="Domains" src="https://img.shields.io/badge/domains-5-purple"></a>
  <a href="#排行榜"><img alt="Models" src="https://img.shields.io/badge/models-8-orange"></a>
  <a href="#排行榜"><img alt="Harnesses" src="https://img.shields.io/badge/harnesses-4-blue"></a>
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
- **Harness 无关。** 同一批任务可在 ClaudeCode、OpenClaw、Hermes、Codex 或任意通过 Docker 接入的 Agent 框架上运行。
- **隔离可复现。** 每个任务在独立 Docker 容器内运行，输入文件按需注入；评分脚本对 Agent 不可见。

---

## 排行榜

完整交互式排行榜：[polyworkbench.github.io](https://polyworkbench.github.io/)

> **32 个模型&times;Harness 组合**（8 个基础模型 &times; 4 种 Harness：ClaudeCode、OpenClaw、Hermes、Codex），每个组合最多 3 次完整运行。
> **Pass@1** = 全部 67 个任务上的最佳单次运行平均 Grade（主排名指标）；**Pass@3** = 每任务取三次运行最优后的平均 Grade。
> 分域（COM / KNW / LEG / LOC / MFG）与逐条目的 Judge 分数见交互式排行榜。

### 主要结果 —— Pass@1（Pass@3）

| 模型 | ClaudeCode | OpenClaw | Hermes | Codex |
|------|:----------:|:--------:|:------:|:-----:|
| **Claude Opus 4.8** | **0.923**（0.927） | 0.778（0.850） | 0.805（0.827） | 0.698（0.786） |
| GLM-5.2 | 0.855（0.895） | 0.853（0.893） | 0.823（0.875） | 0.887（0.918） |
| GLM-5.1 | 0.785（0.789） | 0.783（0.798） | 0.790（0.814） | 0.781（0.801） |
| DeepSeek V4 Flash | 0.796（0.814） | 0.708（0.755） | 0.758（0.828） | 0.797（0.835） |
| GPT-5.5 | 0.815（0.815） | 0.794（0.917） | 0.837（0.906） | 0.808（0.905） |
| Qwen3.6-35B-A3B | 0.793（0.824） | 0.673（0.746） | 0.727（0.804） | 0.682（0.822） |
| Claude Opus 4.7 | 0.797（0.827） | 0.709（0.763） | 0.800（0.849） | 0.612（0.765） |
| Qwen3.6-27B | 0.801（0.814） | 0.782（0.805） | 0.742（0.801） | 0.766（0.824） |

**加粗** = 综合最佳：**Claude Opus 4.8 + ClaudeCode**（Pass@1 0.923 / Pass@3 0.927）。

### 关键结论

- **即使对前沿模型，该基准也很有挑战性。** 最佳组合 Pass@1 0.923 / Pass@3 0.927；第二名（GLM-5.2 &times; Codex）为 0.887 / 0.918。
- **Harness 的选择影响显著，但并非对所有模型一致。** Claude Opus 4.8 在四种 Harness 间 Pass@1 跨度达 0.225（ClaudeCode 0.923 &rarr; Codex 0.698），而 GLM-5.1 几乎与 Harness 无关（跨度 &le; 0.009）。
- **Commerce 是系统性短板。** 全能型强模型在知识/法律/制造上保持 0.85&ndash;0.95 的 Grade，却在 Commerce 上掉到 0.57&ndash;0.72（严格的数值核对与表格结构类任务）。
- **语言是真实的失败维度。** Claude Opus 4.8/ClaudeCode 在十种语言上表现均衡（0.83&ndash;0.97），而中档模型在俄语、西班牙语和德语上显著退化；同一模型最佳与最差语言之间的 Grade 差距可超过 30 分。
- **Judge 是诊断信号，不是排名指标。** 平均 Judge 集中在 0.73&ndash;0.84 的窄区间，与 Grade 仅弱相关（r &asymp; 0.23）；而 Grade 与 Pytest 强一致（r = 0.88）。
- **Pass@3 的增益在头部很小**（Opus 4.8/ClaudeCode 仅 +0.004），在中档条目上变大（Qwen3.6-35B-A3B/Codex 达 +0.140）。

---

## 任务总览

67 个任务横跨 5 大领域、10 种语言。平均每个任务携带 **3.4 个输入文件、跨 2.3 种不同语言**，其参考规范包含 **6.2 个加权结构化子分**，共同构成任务级 Grade（依据论文）。

### 领域分布

| 领域 | 任务数 | 描述 | 示例 |
|------|:-----:|------|------|
| **COM**（商业） | 16 | 跨境运营、定价、物流、税务、市场管理 | 多币种对账，识别预埋差异 |
| **KNW**（知识） | 11 | 信息综合、技术报告、专利分析、多语言事实核查 | 跨语言事实核查，需用到全部语言来源 |
| **LEG**（法律） | 15 | 合规分析、合同审查、法规对比、法律起草 | 德文合同冲突检测（预埋条款冲突） |
| **LOC**（本地化） | 11 | 软件、文档、字幕、营销材料的多语言适配 | 跨平台 UI 文案不一致检测 |
| **MFG**（制造） | 14 | 质量管理、生产报告、维护、安全审计、供应链分析 | 跨韩/中/英日志做时间戳关联以定位根因 |

### 语言覆盖（主指令语言）

| 语言 | 任务数 | 语言 | 任务数 |
|------|:-----:|------|:-----:|
| 韩语 (ko) | 13 | 中文 (zh) | 6 |
| 英语 (en) | 10 | 多语言混合 (multi) | 5 |
| 俄语 (ru) | 7 | 西班牙语 (es) | 4 |
| 日语 (ja) | 6 | 德语 (de) | 3 |
| 越南语 (vi) | 6 | 阿拉伯语 (ar) | 1 |
| 法语 (fr) | 6 | | |

> &ldquo;multi&rdquo; = 指令交织两种及以上语言、无单一主导语言的任务。阿拉伯语（n=1）为探索性单实例任务，按论文约定不纳入对比统计。许多任务的资源语言与输出语言独立于指令语言选择。

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
|  轨 1：Grade   -> 0-1.0 加权结构化子分                    |
|  轨 2：Pytest  -> 通过单元测试的比例                       |
|  轨 3：Judge   -> 0-1.0 LLM-as-Judge 语义评估             |
+---------------------------------------------------------+
排名指标：Grade，以 Pass@1（最佳单次运行均值）与 Pass@3（每任务取三次最优）报告
- Grade：任务专属加权结构化子分（合计 1.0），由确定性脚本对磁盘产物打分
- Pytest：同一套评分规范表达为通过/失败单元测试；得分 = 通过比例（不调用 LLM）
- Judge：固定提示词，对 4 个维度（模态保真、语言准确、任务完成、长程一致性）取平均；仅作诊断信号，不参与排名
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

运行全部 67 任务 x 3 轮，产出 Pass@3（每任务三次最优）统计指标：
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
@misc{li2026polyworkbenchbenchmarkingllmagents,
      title={PolyWorkBench: Benchmarking LLM Agents for Cross-Lingual Long-Horizon Workflows}, 
      author={Hongliang Li and Yijin Liu and Zhiwei Zhang and Zihe Liu and Xinyue Lou and Jinan Xu and Fandong Meng and Kaiyu Huang},
      year={2026},
      eprint={2607.06008},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2607.06008}, 
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
