<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/hero_banner_dark.svg">
    <img src="diagrams/hero_banner_light.svg" alt="AICertify — Compliance-as-code for AI systems" width="100%">
  </picture>
</div>

<p align="center">
  <a href="README.md">English</a> |
  <strong>简体中文</strong> |
  <a href="README.ja-JP.md">日本語</a> |
  <a href="README.ko-KR.md">한국어</a> |
  <a href="README.hi-IN.md">हिन्दी</a>
</p>

<p align="center">
  <em>依据 EU AI Act、NIST AI RMF,以及另外 6 个国际框架审计您的 AI:一份合约,一条命令,一份报告。</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/aicertify/"><img src="https://img.shields.io/pypi/v/aicertify?style=flat-square&color=blue" alt="PyPI"></a>
  <a href="https://pepy.tech/project/aicertify"><img src="https://img.shields.io/pepy/dt/aicertify?style=flat-square" alt="下载量"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml"><img src="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml/badge.svg" alt="持续集成"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/stargazers"><img src="https://img.shields.io/github/stars/Principled-Evolution/aicertify?style=flat-square" alt="Star 数"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12-blue.svg?style=flat-square" alt="Python 3.12"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square" alt="Apache 2.0 许可证"></a>
  <a href="https://www.openpolicyagent.org/ecosystem/entry/principled-evolution"><img src="https://img.shields.io/badge/built%20on-OPA-7D4698.svg?style=flat-square" alt="基于 OPA 构建"></a>
  <a href="https://github.com/Principled-Evolution/gopal"><img src="https://img.shields.io/badge/policies-92%20rego-2f9e44.svg?style=flat-square" alt="92 条 Rego 策略"></a>
  <a href="https://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="欢迎提交 PR"></a>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram1_hero_flow_dark.svg">
    <img src="diagrams/diagram1_hero_flow_light.svg" alt="从 AI 应用到审计就绪的报告:AI 应用 -> AICertify 合约 -> OPA 策略评估 -> 合规报告" width="85%" />
  </picture>
</p>

<br>

监管机构推进的速度比您的治理文档更快。EU AI Act 已经生效。NIST AI RMF 已成为美国事实上的标准。印度、巴西和新加坡也将紧随其后。`AICertify` 让您能够将这些义务编码为可执行的 [Open Policy Agent](https://www.openpolicyagent.org/) 策略,在采集到的 AI 交互数据上运行,并生成 PDF、Markdown、JSON 或 HTML 格式的审计就绪报告。

它是连接"我们有负责任的 AI 策略"与"我们能够证明这一点"之间缺失的一环。

**适用场景包括:**

- 把 AI 治理政策转化为可执行的检查项
- 在每次发布时产出审计就绪的合规证据
- 依据具名法规框架评估 AI 交互(EU AI Act、NIST AI RMF、FERPA、公平借贷、FAA/EASA 航空法规等)
- 生成审计人员可以直接阅读的 Markdown、JSON、HTML 或 PDF 报告
- 把 AI 合规检查接入 CI/CD 流程

AICertify 是 [Open Policy Agent 生态系统](https://www.openpolicyagent.org/ecosystem/entry/principled-evolution)的一员,构建于支撑 Kubernetes 准入控制、微服务鉴权以及大规模基础设施治理的同一套策略引擎之上。

> ⭐ **如果 AICertify 对您有帮助,请为本仓库点亮 star。** 这能帮助更多 AI 治理和策略即代码从业者发现这个项目。

---

## 快速开始

```bash
# 1. 安装 AICertify(首次安装约需 3–5 分钟,会拉取 langchain 与 transformers)
pip install aicertify

# 2. 安装 OPA 二进制文件,只需一次(约 80 MB)
curl -L https://openpolicyagent.org/downloads/latest/opa_linux_amd64 -o /usr/local/bin/opa && sudo chmod +x /usr/local/bin/opa

# 3. 运行内置演示(无需合约文件,无需 API key,约 10 秒)
aicertify demo
```

`aicertify demo` 会加载内置的示例合约,通过 OPA 依据 EU AI Act 策略集对其进行评估,并将 `aicertify_demo_report.md` 写入当前目录。打开这份报告:这就是您的审计交付物的样子。

<p align="center">
  <img src="docs/demo.gif" alt="aicertify demo 运行录屏:横幅信息、加载动画、评估进度与生成的报告路径" width="85%" />
</p>

如需更完整的评估(LangFair 公平性指标、DeepEval 内容安全评分、PDF 报告),请查看 [`examples/quickstart.py`](examples/quickstart.py),以及[可派生的示例机器人](examples/),每个示例都包含 `input_contract.json`、`policy_config.yaml` 和 `run.py`。

### 用于开发

```bash
git clone https://github.com/Principled-Evolution/aicertify.git
cd aicertify
pip install -e .
```

### 最简 Python 用法

```python
from aicertify import regulations, application

# 1. 选择需要认证的法规
regs = regulations.create("my_regulations")
regs.add("eu_ai_act")

# 2. 包装您的 AI 应用
app = application.create(
    name="customer-support-bot",
    model_name="gpt-4o",
    model_version="2024-08-06",
)

# 3. 输入真实的交互数据
app.add_interaction(
    input_text="I want a refund for my order",
    output_text="I can help with that. Could you share your order number?",
)

# 4. 评估并取回报告
await app.evaluate(regulations=regs, report_format="pdf", output_dir="reports")
```

整个闭环就这么简单。**合约 → 交互 → 评估 → 报告。**

---

## 为何选择 AICertify

目前的 AI 治理工具大致分为两类:

- **厂商 SaaS**,把您的审计轨迹锁在登录页后面(Credo AI、Holistic AI),或
- **研究工具包**,只聚焦单一维度:公平性指标(Fairlearn、AI Fairness 360)或可解释性(Microsoft RAI Toolbox)。

这两类都拿不出监管机构真正想要的东西:*证明您依据某项具名法规测试过这个 AI 系统的证据,包含可复现的策略与带日期的报告。*

AICertify 正是为这份交付物而生。

| | AICertify | Fairlearn / AIF360 | MS RAI Toolbox | Credo AI |
|---|---|---|---|---|
| 开源 | ✅ Apache 2.0 | ✅ MIT | ✅ MIT | ❌ 闭源 |
| 本地部署 / 内网隔离 | ✅ | ✅ | ✅ | ❌ |
| 具名法规框架 | **EU AI Act、NIST RMF、Brazil AI Bill、India Digital Policy,另有 9 个** | ❌(仅公平性) | ❌(工具包) | ✅ |
| 策略即代码(可审计、可对比) | ✅ OPA / Rego | ❌ | ❌ | ❌ |
| 开箱即用的行业垂直领域 | 航空、银行、医疗、汽车、教育 | ❌ | ❌ | 部分 |
| 生成审计就绪报告 | ✅ PDF / MD / JSON / HTML | ❌ | 部分 | ✅ |
| 自定义策略 | ✅ 放入一个 `.rego` 文件即可 | ❌ | 不适用 | ✅(付费) |

---

## 工作原理

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram2_architecture_dark.svg">
    <img src="diagrams/diagram2_architecture_light.svg" alt="AICertify 架构:您的 AI 应用提供合约,合约流经评估器(Fairness、ContentSafety、RiskManagement、Compliance)进入承载 85 条 Rego 策略的 OPA 引擎,并通过报告生成器产出审计交付物" width="85%" />
  </picture>
</p>

1. **合约(Contract)**:用 JSON 描述您的 AI 应用,包括模型、版本、采集到的交互与元数据。
2. **评估器(Evaluators)**:可插拔的 Python 评估器(Fairness、ContentSafety、RiskManagement、Compliance),从交互数据中提取指标。
3. **OPA 策略**:这些指标会依据法规对应的 Rego 策略进行评估(策略来自 [gopal](https://github.com/Principled-Evolution/gopal) 策略库)。
4. **报告**:一份格式化、带日期的交付物,可以直接交给法务、审计师或 AI 风险委员会。

由于策略是声明式的 Rego,它们可以像任何代码一样进行版本管理、差异比对和评审。法规变更时,您只需升级策略,而不必修改评估流水线。

---

## 法规覆盖

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram3_regulatory_coverage_dark.svg">
    <img src="diagrams/diagram3_regulatory_coverage_light.svg" alt="法规覆盖:85 条策略,覆盖 8 个框架与 5 个行业,包括 EU AI Act、NIST AI RMF、India Digital Policy、Brazil AI Bill、RTCA DO-365、FAA Part 107、EASA SORA、ICAO Doc 10019、医疗、银行与金融服务、汽车、教育、全球、航空、AIOps、企业" width="85%" />
  </picture>
</p>

AICertify 基于 [gopal](https://github.com/Principled-Evolution/gopal) 策略库运行,包含 **85 条生产级 OPA 策略**,覆盖以下框架:

### 国际

- **EU AI Act**(29 条策略):禁止性实践、生物识别、操纵行为、透明度、技术文档、人类监督、GPAI 义务。其中多个义务领域目前仍是等待补全逻辑的脚手架(scaffold),具体哪些条款已经可执行,请查看 [gopal 的覆盖矩阵](https://github.com/Principled-Evolution/gopal/blob/main/docs/coverage/eu-ai-act.md)。
- **NIST AI RMF**:Govern、Map、Measure、Manage,以及 AI 600-1
- **India Digital Policy**:对齐 NITI Aayog 发布的《国家人工智能战略》(National Strategy for Artificial Intelligence)。需要说明的是,这并不是另一部单独的 India DPDP 法案,该法案目前尚未纳入覆盖范围
- **Brazil AI Governance Bill**:算法治理要求
- **航空标准**(7 条策略):ICAO Doc 10019、FAA Part 107、FAA Remote ID、EASA Regulation 2019/947、EASA SORA、RTCA DO-365、ISO 21384

### 行业专属

- **航空**(12 条策略):适航性、自主系统、数据管理、飞行运行
- **教育**(12 条策略):FERPA、COPPA、在线监考、人类参与的评分
- **银行与金融服务**:模型风险、公平借贷
- **医疗**:患者安全、诊断安全
- **汽车**:车辆安全集成

### 全球与运营

- **全球**:问责、公平、透明、可解释性、内容安全、风险管理、安全
- **企业**:信息安全、治理
- **AIOps 与成本**:可扩展性、资源效率

全球与运营这两个类别目前大多数仍处于脚手架(scaffold)阶段(包路径已经稳定,但尚不具备可执行的合规逻辑)。在生产环境中使用前,请先查阅上文链接的覆盖矩阵,或直接查看策略文件本身进行确认。

没有看到您需要的法规?[添加一个 Rego 文件](https://github.com/Principled-Evolution/gopal/blob/main/CONTRIBUTING.md)即可。这个策略库本来就是为可扩展而设计的。

---

## 命令行(CLI)

```bash
python -m aicertify.cli \
  --contract path/to/contract.json \
  --policy aicertify/opa_policies/international/eu_ai_act/v1 \
  --report-format pdf \
  --output-dir reports/
```

常用参数:

| 参数 | 用途 |
|---|---|
| `--contract` | AI 应用合约 JSON 的路径 |
| `--policy` | 用于评估的 OPA 策略目录路径 |
| `--report-format` | `pdf`、`markdown`、`json`、`html`(默认:`pdf`) |
| `--output-dir` | 报告输出目录(默认:`./reports`) |
| `--verbose` | 输出详细日志 |

完整的 Python API 请参阅 [`examples/quickstart.py`](examples/quickstart.py)。

---

## 查看输出

不需要安装任何东西,您就能看到 AICertify 产出的效果:仓库里已经提交了预先生成好的报告。

- **[demo-report-eu-ai-act.pdf](docs/demo-report-eu-ai-act.pdf)**:一个客户支持智能体依据 EU AI Act 的评估报告
- [examples/outputs/eu_ai_act/](examples/outputs/eu_ai_act/):标准的完整输出示例
- [examples/outputs/loan_evaluation/](examples/outputs/loan_evaluation/):一个信用评分模型的公平借贷评估
- [examples/outputs/medical_diagnosis/](examples/outputs/medical_diagnosis/):一个临床决策支持模型的患者安全评估

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram5_report_anatomy_dark.svg">
    <img src="diagrams/diagram5_report_anatomy_light.svg" alt="审计就绪报告的结构剖析:包含框架名称、应用、模型与日期的页眉;执行摘要;策略结果表;风险评估柱状图;整改建议;以及标注 AICertify v0.8.0 的页脚" width="85%" />
  </picture>
</p>

打开这些 PDF,这正是审计师想要看到的样子。

---

## 状态

AICertify 目前处于 **beta 阶段(v0.8.0)**。1.0 正式版发布前,API 仍可能发生变化。当前已可用于生产的框架情况如下:

- ✅ 全球评估器(公平性、内容安全、透明度):全部 9 条策略均已实现
- ✅ 航空策略集(ICAO、FAA、EASA、RTCA、ISO):全部 19 条策略均已实现,覆盖国际监管标准与行业垂直两个类别
- ✅ 汽车:车辆安全已完整实现
- 🚧 EU AI Act:29 条策略中已实现 8 条,其余仍是等待补上真实逻辑的脚手架
- 🚧 NIST AI RMF:Govern 与 AI 600-1 编排器已实现,Map、Measure、Manage 仍是脚手架
- 🚧 医疗、银行与金融服务(BFS):两个领域各自实现了一条策略(诊断安全、公平借贷),另一条仍是脚手架(患者安全、模型风险)
- 🚧 India Digital Policy:仍处于早期阶段

所谓"脚手架(scaffold)",是指包路径与默认拒绝(default-deny)结构已经就绪,但合规逻辑尚未写完,因此策略会始终返回拒绝结果。逐条义务的具体落实情况请参见 [gopal 的覆盖矩阵](https://github.com/Principled-Evolution/gopal/tree/main/docs/coverage),后续计划请参见[策略库路线图](https://github.com/Principled-Evolution/gopal)。

---

## 面向 OPA / Rego 用户

如果您已经在用 OPA 处理 Kubernetes 准入控制、微服务鉴权或基础设施治理,那么 AICertify 就是您现有策略体系里补上的 AI 系统这一环。

- **带上您自己的 Rego 策略。** 把 `.rego` 文件放进策略目录,它就会和内置策略集一起被评估。
- **通过 OPA 评估 AI 交互。** 采集到的输入、输出与指标,会通过标准的 OPA `input` 文档流入您的策略。
- **生成审计就绪的证据。** PDF / Markdown / JSON / HTML,一条命令搞定。
- **底层使用 [gopal](https://github.com/Principled-Evolution/gopal) 作为策略库。** 85 条生产级 Rego 策略,覆盖 EU AI Act、NIST AI RMF、航空安全、FERPA、公平借贷等。

AICertify 已被收录进 [Open Policy Agent 生态系统](https://www.openpolicyagent.org/ecosystem/entry/principled-evolution),是与 Gopal 并列的 AI 治理条目。

---

## 为什么是 AICertify?

大多数 AI 治理项目都停留在 PDF、电子表格和政策文档里,它们描述的是*应该*发生什么,却证明不了*实际*发生了什么。

AICertify 把治理规则变成可执行的策略检查。

与其说:

> "我们的聊天机器人遵循负责任 AI 政策。"

不如拿出:

> "这是采集到的交互记录、策略版本、OPA 评估结果,以及生成的审计报告。"

AICertify 服务于 AI 团队、治理团队、审计人员以及平台工程师,他们需要的 AI 合规证据必须**可读、可运行、可审阅、可复现**。

完整的定位说明请见 [docs/why-aicertify.md](docs/why-aicertify.md)。

---

## 谁适合参与贡献?

AICertify 尤其适合以下人群:

- **AI 工程师**:构建受监管的 AI 系统
- **治理、风险与合规(GRC)团队**:产出审计证据
- **审计人员与模型风险专家**:评估第三方 AI
- **OPA / Rego 用户**:对编写 AI 专属策略感兴趣
- **负责任 AI 研究者**:需要可复现的基准测试
- **Python 开发者**:对合规自动化感兴趣

**非代码类贡献同样欢迎:** 示例、策略映射、文档、测试、报告模板,以及法规解读笔记。

推荐从 [good first issue](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) 和 [help wanted](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) 这两个标签入手。

---

## 参与贡献

我们欢迎:

- 新的法规框架(请先开 issue 对齐范围)
- 您已经在实践中验证过的行业专属策略
- 新的评估器(公平性、安全性、鲁棒性,参见 `aicertify/evaluators/`)
- 附带最小可复现合约的缺陷报告
- 文档、示例与教程

请从 [CONTRIBUTING.md](CONTRIBUTING.md)、[行为准则](CODE_OF_CONDUCT.md)以及公开的[贡献者 issue 列表](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)开始。

安全问题请遵循[安全策略](SECURITY.md):私下报告至 [security@principledevolution.ai](mailto:security@principledevolution.ai),不要通过公开 issue 提交。

---

## 相关项目

- **[gopal](https://github.com/Principled-Evolution/gopal)**:AICertify 底层使用的 OPA 策略库。如果不需要 Python 框架,也可以搭配 OPA CLI 单独使用。
- **[Open Policy Agent](https://www.openpolicyagent.org/)**:策略引擎本身。
- **[Regal](https://github.com/StyraInc/regal)**:用来保持策略整洁的 Rego 代码检查工具。

---

## 许可证

Apache License 2.0,详见 [LICENSE](LICENSE)。

---

<p align="center">
  <strong>⭐ 如果 AICertify 对您有用,请为仓库点亮 star,并分享给一位同事。</strong><br>
  <sub>每一个 star 都能帮助更多 AI 治理和策略即代码从业者发现这个项目。</sub>
</p>

<p align="center"><sub>由 <a href="https://github.com/Principled-Evolution">Principled Evolution</a> 构建 · 可读、可运行、可证明的策略。</sub></p>
