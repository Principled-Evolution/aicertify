<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/hero_banner_dark.svg">
    <img src="diagrams/hero_banner_light.svg" alt="AICertify — Compliance-as-code for AI systems" width="100%">
  </picture>
</div>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.ja-JP.md">日本語</a> |
  <strong>한국어</strong> |
  <a href="README.hi-IN.md">हिन्दी</a>
</p>

<p align="center">
  <em>EU AI Act, NIST AI RMF를 비롯한 6개의 추가 국제 프레임워크에 대해 AI를 감사합니다: 하나의 계약, 하나의 명령, 하나의 리포트.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/aicertify/"><img src="https://img.shields.io/pypi/v/aicertify?style=flat-square&color=blue" alt="PyPI"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml"><img src="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/stargazers"><img src="https://img.shields.io/github/stars/Principled-Evolution/aicertify?style=flat-square" alt="Stars"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12%2B-blue.svg?style=flat-square" alt="Python 3.12+"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square" alt="Apache 2.0"></a>
  <a href="https://www.openpolicyagent.org/ecosystem/entry/principled-evolution"><img src="https://img.shields.io/badge/built%20on-OPA-7D4698.svg?style=flat-square" alt="Built on OPA"></a>
  <a href="https://github.com/Principled-Evolution/gopal"><img src="https://img.shields.io/badge/policies-85%20rego-2f9e44.svg?style=flat-square" alt="85 Rego Policies"></a>
  <a href="https://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome"></a>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram1_hero_flow_dark.svg">
    <img src="diagrams/diagram1_hero_flow_light.svg" alt="AI 애플리케이션에서 감사 준비 리포트까지: AI 애플리케이션 -> AICertify 계약 -> OPA 정책 평가 -> 컴플라이언스 리포트" width="85%" />
  </picture>
</p>

<br>

규제는 거버넌스 문서보다 빠르게 움직이고 있습니다. EU AI Act는 발효되었고, NIST AI RMF는 미국의 사실상 표준이 되었습니다. 인도, 브라질, 싱가포르가 그 뒤를 잇고 있습니다. `AICertify`는 이러한 의무를 실행 가능한 [Open Policy Agent](https://www.openpolicyagent.org/) 정책으로 인코딩하고, 수집된 AI 상호작용에 대해 실행하며, PDF, Markdown, JSON 또는 HTML 형식의 감사 준비 리포트를 생성할 수 있게 해줍니다.

이는 *"우리에게는 책임 있는 AI 정책이 있다"* 와 *"우리는 그것을 증명할 수 있다"* 사이의 잃어버린 연결고리입니다.

**다음과 같은 작업이 필요할 때 사용하세요:**

- AI 거버넌스 정책을 실행 가능한 체크로 전환합니다
- 릴리스마다 감사 준비가 된 컴플라이언스 증거를 생성합니다
- 명명된 규제 프레임워크(EU AI Act, NIST AI RMF, FERPA, 공정 대출, FAA/EASA 항공 등)에 대해 AI 상호작용을 평가합니다
- 감사관이 읽을 수 있는 Markdown, JSON, HTML, PDF 리포트를 생성합니다
- AI 컴플라이언스 체크를 CI/CD에 통합합니다

AICertify는 [Open Policy Agent 에코시스템](https://www.openpolicyagent.org/ecosystem/entry/principled-evolution)의 일원으로, Kubernetes 어드미션 컨트롤, 마이크로서비스 인가, 대규모 인프라 거버넌스를 지탱하는 것과 동일한 정책 엔진 위에 구축되었습니다.

> ⭐ **AICertify가 도움이 되었다면 리포지토리에 스타를 눌러 주세요.** AI 거버넌스와 정책 코드화(policy-as-code) 실무자들이 이 프로젝트를 발견하는 데 도움이 됩니다.

---

## 빠른 시작

```bash
# 1. AICertify 설치 (첫 설치는 약 3~5분 소요, langchain + transformers 다운로드)
pip install aicertify

# 2. OPA 바이너리 일회성 설치 (약 80 MB)
curl -L https://openpolicyagent.org/downloads/latest/opa_linux_amd64 -o /usr/local/bin/opa && sudo chmod +x /usr/local/bin/opa

# 3. 번들 데모 실행 (계약 파일 불필요, API 키 불필요, 약 10초)
aicertify demo
```

`aicertify demo`는 번들 샘플 계약을 로드하여 OPA를 통해 EU AI Act 정책 세트에 대해 평가하고, 현재 디렉터리에 `aicertify_demo_report.md` 파일을 작성합니다. 리포트를 열어 보세요. 그것이 바로 감사 산출물의 모습입니다.

<p align="center">
  <img src="docs/demo.gif" alt="aicertify demo 실행 녹화: 배너, 스피너, 평가 진행 상황, 생성된 리포트 경로" width="85%" />
</p>

더 풍부한 평가(LangFair 공정성 지표, DeepEval 콘텐츠 안전성 스코어링, PDF 리포트)는 [`examples/quickstart.py`](examples/quickstart.py)와 [포크 가능한 예시 봇들](examples/)을 참고하세요. 각 예시에는 `input_contract.json`, `policy_config.yaml`, `run.py`가 포함되어 있습니다.

### 개발용 설치

```bash
git clone https://github.com/Principled-Evolution/aicertify.git
cd aicertify
pip install -e .
```

### 최소 Python 사용 예시

```python
from aicertify import regulations, application

# 1. 인증받을 규제를 선택합니다
regs = regulations.create("my_regulations")
regs.add("eu_ai_act")

# 2. AI 앱을 래핑합니다
app = application.create(
    name="customer-support-bot",
    model_name="gpt-4o",
    model_version="2024-08-06",
)

# 3. 실제 상호작용을 입력합니다
app.add_interaction(
    input_text="I want a refund for my order",
    output_text="I can help with that. Could you share your order number?",
)

# 4. 평가 후 리포트를 받습니다
await app.evaluate(regulations=regs, report_format="pdf", output_dir="reports")
```

이것이 전체 흐름입니다. **계약 → 상호작용 → 평가 → 리포트.**

---

## AICertify를 선택해야 하는 이유

대부분의 AI 거버넌스 도구는 다음 중 하나입니다.

- **벤더 SaaS**: 감사 추적을 로그인 뒤에 가두어 둡니다(Credo AI, Holistic AI).
- **연구용 툴킷**: 공정성 지표(Fairlearn, AI Fairness 360)나 설명 가능성(Microsoft RAI Toolbox)과 같은 단일 차원에만 집중합니다.

이 중 어느 것도 규제 당국이 실제로 요구하는 문서, 즉 *명시된 규제에 대해 이 AI 시스템을 테스트했다는 증거, 재현 가능한 정책과 날짜가 기재된 리포트* 를 만들어 내지 못합니다.

AICertify는 바로 그 산출물을 위해 만들어졌습니다.

| | AICertify | Fairlearn / AIF360 | MS RAI Toolbox | Credo AI |
|---|---|---|---|---|
| 오픈소스 | ✅ Apache 2.0 | ✅ MIT | ✅ MIT | ❌ 비공개 |
| 온프레미스 / 에어갭 환경 | ✅ | ✅ | ✅ | ❌ |
| 명명된 규제 프레임워크 | **EU AI Act, NIST RMF, Brazil AI Bill, India Digital Policy, +9개 더** | ❌ (공정성만 해당) | ❌ (툴킷) | ✅ |
| 정책 코드화 (감사 가능, 비교 가능) | ✅ OPA / Rego | ❌ | ❌ | ❌ |
| 기본 제공 산업 수직 영역 | 항공, 금융, 의료, 자동차, 교육 | ❌ | ❌ | 일부 |
| 감사 준비 리포트 생성 | ✅ PDF / MD / JSON / HTML | ❌ | 일부 | ✅ |
| 맞춤형 정책 | ✅ `.rego` 파일 추가만으로 가능 | ❌ | 해당 없음 | ✅ (유료) |

---

## 작동 방식

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram2_architecture_dark.svg">
    <img src="diagrams/diagram2_architecture_light.svg" alt="AICertify 아키텍처: AI 앱이 계약을 제공하고, 이는 평가기(Fairness, ContentSafety, RiskManagement, Compliance)를 거쳐 85개의 Rego 정책을 포함한 OPA 엔진으로 흐르며, 리포트 생성기를 통해 감사 산출물을 만들어 냅니다" width="85%" />
  </picture>
</p>

1. **계약(Contract)**: AI 애플리케이션을 설명하는 JSON입니다. 모델, 버전, 수집된 상호작용, 메타데이터를 포함합니다.
2. **평가기(Evaluators)**: 플러그형 Python 평가기(Fairness, ContentSafety, RiskManagement, Compliance)가 상호작용에서 메트릭을 추출합니다.
3. **OPA 정책**: 메트릭은 규제의 Rego 정책에 대해 평가됩니다([gopal](https://github.com/Principled-Evolution/gopal) 정책 라이브러리에서 제공).
4. **리포트**: 법무팀, 감사관 또는 AI 리스크 위원회에 전달할 수 있는 형식화되고 날짜가 기재된 산출물입니다.

정책이 선언적 Rego이기 때문에, 다른 코드와 마찬가지로 버전 관리, 차이 비교, 리뷰가 가능합니다. 규제가 변경되면 평가 하네스가 아닌 정책을 업데이트하기만 하면 됩니다.

---

## 규제 커버리지

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram3_regulatory_coverage_dark.svg">
    <img src="diagrams/diagram3_regulatory_coverage_light.svg" alt="규제 커버리지: 8개 프레임워크와 5개 산업에 걸친 85개 정책 -- EU AI Act, NIST AI RMF, India Digital Policy, Brazil AI Bill, RTCA DO-365, FAA Part 107, EASA SORA, ICAO Doc 10019, 의료, 은행 및 금융, 자동차, 교육, 글로벌, 항공, AIOps, 기업" width="85%" />
  </picture>
</p>

AICertify는 [gopal](https://github.com/Principled-Evolution/gopal) 정책 라이브러리(프로덕션 수준의 **85개 OPA 정책**)를 기반으로, 다음 프레임워크에 대한 평가를 실행합니다.

### 국제
- **EU AI Act** (29개 정책): 금지된 관행, 생체 인식, 조작, 투명성, 기술 문서, 인간의 감독, GPAI 의무 사항을 포함합니다. 여러 의무 영역은 아직 본격 구현을 기다리는 스캐폴드 상태이며, 현재 어떤 항목이 실제로 강제되는지는 [gopal의 커버리지 매트릭스](https://github.com/Principled-Evolution/gopal/blob/main/docs/coverage/eu-ai-act.md)를 참고하세요.
- **NIST AI RMF**: Govern, Map, Measure, Manage + AI 600-1
- **India Digital Policy**: NITI Aayog의 국가 인공지능 전략(National Strategy for Artificial Intelligence)에 맞춰져 있습니다(별도의 India DPDP 법은 아직 다루지 않습니다)
- **Brazil AI Governance Bill**: 알고리즘 거버넌스 요구사항
- **항공 표준** (7개 정책): ICAO Doc 10019, FAA Part 107, FAA Remote ID, EASA Regulation 2019/947, EASA SORA, RTCA DO-365, ISO 21384

### 산업별
- **항공** (12개 정책): 감항성, 자율 시스템, 데이터 관리, 운항
- **교육** (12개 정책): FERPA, COPPA, 시험 감독, 사람이 참여하는 채점
- **은행 및 금융 서비스**: 모델 리스크, 공정 대출
- **의료**: 환자 안전, 진단 안전
- **자동차**: 차량 안전 통합

### 글로벌 및 운영
- **글로벌**: 책임성, 공정성, 투명성, 설명 가능성, 콘텐츠 안전, 리스크 관리, 보안
- **기업**: 정보 보안, 거버넌스
- **AIOps 및 비용**: 확장성, 리소스 효율성

글로벌 및 운영 카테고리는 대부분 아직 스캐폴드(패키지 경로는 안정적으로 갖춰졌지만 강제 가능한 로직은 없는 상태) 단계입니다. 프로덕션에서 의존하기 전에 연결된 커버리지 매트릭스나 정책 파일 자체를 확인하세요.

찾는 규제가 보이지 않나요? [Rego 파일을 추가하세요](https://github.com/Principled-Evolution/gopal/blob/main/CONTRIBUTING.md). 이 라이브러리는 확장 가능하도록 설계되었습니다.

---

## CLI

```bash
python -m aicertify.cli \
  --contract path/to/contract.json \
  --policy aicertify/opa_policies/international/eu_ai_act/v1 \
  --report-format pdf \
  --output-dir reports/
```

유용한 플래그:

| 플래그 | 용도 |
|---|---|
| `--contract` | AI 애플리케이션 계약 JSON 파일 경로 |
| `--policy` | 평가에 사용할 OPA 정책 폴더 경로 |
| `--report-format` | `pdf`, `markdown`, `json`, `html` (기본값: `pdf`) |
| `--evaluators` | 특정 평가기로 제한 (예: `Fairness ContentSafety`) |
| `--output-dir` | 리포트 출력 위치 (기본값: `./reports`) |
| `--verbose` | 상세 로깅 |

전체 Python API는 [`examples/quickstart.py`](examples/quickstart.py)를 참고하세요.

---

## 샘플 리포트

아무것도 설치하지 않아도 AICertify가 생성하는 결과물을 확인할 수 있습니다. 미리 생성된 리포트가 리포지토리에 커밋되어 있습니다.

- **[demo-report-eu-ai-act.pdf](docs/demo-report-eu-ai-act.pdf)**: EU AI Act에 대해 평가된 고객 지원 에이전트
- [examples/outputs/eu_ai_act/](examples/outputs/eu_ai_act/): 대표적인 전체 출력 예시
- [examples/outputs/loan_evaluation/](examples/outputs/loan_evaluation/): 공정 대출 관점에서 평가된 신용 평가 모델
- [examples/outputs/medical_diagnosis/](examples/outputs/medical_diagnosis/): 환자 안전 관점에서 평가된 임상 의사 결정 지원 모델

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram5_report_anatomy_dark.svg">
    <img src="diagrams/diagram5_report_anatomy_light.svg" alt="감사 준비 리포트의 구성: 프레임워크 이름, 애플리케이션, 모델, 날짜를 포함한 헤더, 요약 정리, 정책 결과 표, 리스크 평가 막대 차트, 시정 안내, AICertify v0.8.0 표시 푸터" width="85%" />
  </picture>
</p>

PDF를 열어 보세요. 감사관이 원하는 것이 바로 이것입니다.

---

## 상태

AICertify는 현재 **베타(v0.8.0)** 단계이며, 1.0 릴리스 전까지 API가 변경될 수 있습니다. 현재 프로덕션에 사용할 수 있는 프레임워크는 다음과 같습니다.

- ✅ 글로벌 평가기(공정성, 콘텐츠 안전성, 투명성): 9개 정책 모두 구현 완료
- ✅ 항공 정책 세트(ICAO, FAA, EASA, RTCA, ISO): 국제 규제와 산업별 항목을 합쳐 19개 정책 모두 구현 완료
- ✅ 자동차: 차량 안전 완전 구현
- 🚧 EU AI Act: 29개 정책 중 8개 구현 완료, 나머지는 실제 로직 구현을 기다리는 스캐폴드
- 🚧 NIST AI RMF: Govern과 AI 600-1 오케스트레이터는 구현 완료, Map·Measure·Manage는 스캐폴드
- 🚧 의료, BFS: 산업별로 정책 1개씩 구현 완료(진단 안전, 공정 대출), 나머지 1개는 스캐폴드(환자 안전, 모델 리스크)
- 🚧 India Digital Policy: 초기 단계

"스캐폴드"란 패키지 경로와 기본 거부(default-deny) 구조는 갖춰져 있지만 컴플라이언스 로직이 아직 작성되지 않아 항상 거부(deny)되는 상태를 뜻합니다. 의무 항목별 상세 내역은 [gopal의 커버리지 매트릭스](https://github.com/Principled-Evolution/gopal/tree/main/docs/coverage)를, 다음 계획은 [정책 라이브러리 로드맵](https://github.com/Principled-Evolution/gopal)을 참고하세요.

---

## OPA / Rego 사용자를 위한 안내

이미 Kubernetes 어드미션 컨트롤, 마이크로서비스 인가, 인프라 거버넌스에 OPA를 사용하고 있다면, AICertify는 기존 정책 전략에서 AI 시스템 자리를 채워주는 도구입니다.

- **직접 작성한 Rego 정책을 가져올 수 있습니다.** 정책 폴더에 `.rego` 파일을 추가하기만 하면 번들 정책 세트와 함께 평가됩니다.
- **OPA를 통해 AI 상호작용을 평가할 수 있습니다.** 수집된 입력, 출력, 메트릭은 표준 OPA `input` 문서를 통해 정책으로 전달됩니다.
- **감사 준비 증거를 생성할 수 있습니다.** 명령 한 번으로 PDF / Markdown / JSON / HTML을 만듭니다.
- **[gopal](https://github.com/Principled-Evolution/gopal)을 기반 정책 라이브러리로 사용할 수 있습니다.** EU AI Act, NIST AI RMF, 항공 안전, FERPA, 공정 대출 등을 다루는 85개의 프로덕션 Rego 정책입니다.

AICertify는 [Open Policy Agent 에코시스템](https://www.openpolicyagent.org/ecosystem/entry/principled-evolution)에 Gopal과 나란히 AI 거버넌스 항목으로 등재되어 있습니다.

---

## 왜 AICertify인가

대부분의 AI 거버넌스 프로그램은 PDF, 스프레드시트, 정책 문서 안에만 존재합니다. 이런 문서는 *어떻게 되어야 하는지*를 설명할 뿐, *실제로 어떻게 되었는지*는 증명하지 못합니다.

AICertify는 거버넌스 규칙을 실행 가능한 정책 체크로 바꿔줍니다.

다음과 같이 말하는 대신:

> "우리 챗봇은 책임 있는 AI 정책을 따릅니다."

다음을 제시할 수 있습니다.

> "여기 수집된 상호작용, 정책 버전, OPA 평가 결과, 생성된 감사 리포트가 있습니다."

AICertify는 **읽고, 실행하고, 검토하고, 반복할 수 있는** AI 컴플라이언스 증거가 필요한 AI 팀, 거버넌스 팀, 감사관, 플랫폼 엔지니어를 위한 도구입니다.

전체 포지셔닝은 [docs/why-aicertify.md](docs/why-aicertify.md)에서 확인하세요.

---

## 기여에 적합한 사람들

AICertify는 특히 다음과 같은 분들에게 유용합니다.

- 규제 대상 AI 시스템을 구축하는 **AI 엔지니어**
- 감사 증거를 만드는 **거버넌스·리스크·컴플라이언스(GRC) 팀**
- 서드파티 AI를 평가하는 **감사관 및 모델 리스크 전문가**
- AI 특화 정책 작성에 관심 있는 **OPA / Rego 사용자**
- 재현 가능한 벤치마크를 원하는 **책임 있는 AI 연구자**
- 컴플라이언스 자동화에 관심 있는 **Python 개발자**

**코드가 아닌 기여도 환영합니다.** 예제, 정책 매핑, 문서, 테스트, 리포트 템플릿, 규제 관련 노트 등.

시작하기 좋은 지점은 [`good first issue`](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)와 [`help wanted`](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) 라벨입니다.

---

## 기여

다음과 같은 기여를 환영합니다.

- 새로운 규제 프레임워크(범위 정렬을 위해 먼저 이슈를 열어 주세요)
- 현장 검증된 산업별 정책
- 새로운 평가기(공정성, 안전성, 견고성. 자세한 내용은 `aicertify/evaluators/` 참고)
- 최소 재현 가능 계약을 포함한 버그 리포트
- 문서, 예제, 튜토리얼

먼저 [CONTRIBUTING.md](CONTRIBUTING.md), [행동 강령](CODE_OF_CONDUCT.md), 그리고 열려 있는 [컨트리뷰터 이슈](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)를 확인해 주세요.

보안 문제는 공개 이슈가 아니라 [Security Policy](SECURITY.md)에 따라 [security@principledevolution.ai](mailto:security@principledevolution.ai)로 비공개 제보해 주세요.

---

## 관련 프로젝트

- **[gopal](https://github.com/Principled-Evolution/gopal)**: AICertify가 내부적으로 사용하는 OPA 정책 라이브러리입니다. Python 프레임워크가 필요하지 않다면 OPA CLI와 함께 단독으로 사용할 수 있습니다.
- **[Open Policy Agent](https://www.openpolicyagent.org/)**: 정책 엔진입니다.
- **[Regal](https://github.com/StyraInc/regal)**: 정책을 깔끔하게 유지하기 위해 사용하는 Rego 린터입니다.

---

## 라이선스

Apache License 2.0. [LICENSE](LICENSE)를 참고하세요.

---

<p align="center">
  <strong>⭐ AICertify가 유용하다면 리포지토리에 스타를 남기고 동료 한 명에게 공유해 주세요.</strong><br>
  <sub>스타 하나하나가 AI 거버넌스와 정책 코드화 실무자들이 이 프로젝트를 발견하는 데 도움이 됩니다.</sub>
</p>

<p align="center"><sub>Built by <a href="https://github.com/Principled-Evolution">Principled Evolution</a> · 읽고, 실행하고, 증명할 수 있는 정책.</sub></p>
