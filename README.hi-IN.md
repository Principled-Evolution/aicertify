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
  <a href="README.ko-KR.md">한국어</a> |
  <strong>हिन्दी</strong>
</p>

<p align="center">
  <em>अपने AI का ऑडिट EU AI Act, NIST AI RMF, और 6 और अंतर्राष्ट्रीय फ्रेमवर्क्स के विरुद्ध करें: एक कॉन्ट्रैक्ट, एक कमांड, एक रिपोर्ट।</em>
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
    <img src="diagrams/diagram1_hero_flow_light.svg" alt="AI ऐप से ऑडिट-तैयार रिपोर्ट तक: AI Application -> AICertify Contract -> OPA Policy Evaluation -> Compliance Report" width="85%" />
  </picture>
</p>

<br>

रेगुलेटर्स आपके गवर्नेंस डॉक्यूमेंट्स से तेज़ी से आगे बढ़ रहे हैं। EU AI Act लागू हो चुका है। NIST AI RMF अमेरिका का डी-फैक्टो स्टैंडर्ड है। भारत, ब्राज़ील, और सिंगापुर अगले हैं। `AICertify` आपको इन दायित्वों को निष्पादन योग्य [Open Policy Agent](https://www.openpolicyagent.org/) पॉलिसीज़ के रूप में एनकोड करने, कैप्चर की गई AI इंटरैक्शन्स के विरुद्ध चलाने, और PDF, Markdown, JSON, या HTML में ऑडिट-तैयार रिपोर्ट्स तैयार करने की सुविधा देता है।

यह *"हमारे पास एक responsible-AI पॉलिसी है"* और *"हम इसे सिद्ध कर सकते हैं"* के बीच की लुप्त कड़ी है।

**इसका उपयोग तब करें जब आपको ज़रूरत हो:**

- AI गवर्नेंस पॉलिसीज़ को निष्पादन योग्य चेक्स में बदलना
- हर रिलीज़ पर ऑडिट-तैयार कम्प्लायंस एविडेंस तैयार करना
- AI इंटरैक्शन्स का मूल्यांकन नामित रेगुलेटरी फ्रेमवर्क्स (EU AI Act, NIST AI RMF, FERPA, fair-lending, FAA/EASA aviation, …) के विरुद्ध करना
- ऐसी Markdown, JSON, HTML, या PDF रिपोर्ट्स जनरेट करना जिन्हें आपका ऑडिटर पढ़ सके
- AI कम्प्लायंस चेक्स को CI/CD में इंटीग्रेट करना

AICertify [Open Policy Agent ecosystem](https://www.openpolicyagent.org/ecosystem/entry/principled-evolution) का हिस्सा है, उसी पॉलिसी इंजन पर बना है जो बड़े पैमाने पर Kubernetes admission, माइक्रोसर्विस ऑथराइज़ेशन, और इंफ्रास्ट्रक्चर गवर्नेंस को शक्ति देता है।

> ⭐ **यदि AICertify आपके लिए उपयोगी है, तो कृपया रीपो को स्टार करें।** इससे AI गवर्नेंस और policy-as-code प्रैक्टिशनर्स को यह प्रोजेक्ट खोजने में मदद मिलती है।

---

## Quick Start

```bash
# 1. AICertify इंस्टॉल करें (पहली बार इंस्टॉल में ~3–5 मिनट; langchain + transformers डाउनलोड होते हैं)
pip install aicertify

# 2. OPA बाइनरी एक बार इंस्टॉल करें (~80 MB)
curl -L https://openpolicyagent.org/downloads/latest/opa_linux_amd64 -o /usr/local/bin/opa && sudo chmod +x /usr/local/bin/opa

# 3. बंडल्ड डेमो चलाएँ (कोई कॉन्ट्रैक्ट फ़ाइल नहीं, कोई API keys नहीं, ~10 सेकंड)
aicertify demo
```

`aicertify demo` एक बंडल्ड सैंपल कॉन्ट्रैक्ट लोड करता है, उसे OPA के माध्यम से EU AI Act पॉलिसी सेट पर मूल्यांकित करता है, और मौजूदा डायरेक्टरी में `aicertify_demo_report.md` लिखता है। रिपोर्ट खोलिए: यही आपके ऑडिट डिलिवरेबल का स्वरूप है।

<p align="center">
  <img src="docs/demo.gif" alt="aicertify demo रिकॉर्डिंग: बैनर, स्पिनर्स, मूल्यांकन प्रगति, जनरेट की गई रिपोर्ट का पथ" width="85%" />
</p>

विस्तृत मूल्यांकन (LangFair फेयरनेस मेट्रिक्स, DeepEval कंटेंट-सेफ़्टी स्कोरिंग, PDF रिपोर्ट) के लिए [`examples/quickstart.py`](examples/quickstart.py) और [फ़ोर्क-योग्य उदाहरण बॉट्स](examples/) देखें, जिनमें हर एक में `input_contract.json`, `policy_config.yaml`, और `run.py` शामिल हैं।

### डेवलपमेंट के लिए

```bash
git clone https://github.com/Principled-Evolution/aicertify.git
cd aicertify
pip install -e .
```

### न्यूनतम Python उपयोग

```python
from aicertify import regulations, application

# 1. Pick the regulations you want to certify against
regs = regulations.create("my_regulations")
regs.add("eu_ai_act")

# 2. Wrap your AI app
app = application.create(
    name="customer-support-bot",
    model_name="gpt-4o",
    model_version="2024-08-06",
)

# 3. Feed it real interactions
app.add_interaction(
    input_text="I want a refund for my order",
    output_text="I can help with that. Could you share your order number?",
)

# 4. Evaluate and get reports back
await app.evaluate(regulations=regs, report_format="pdf", output_dir="reports")
```

यही पूरा लूप है। **Contract → interactions → evaluate → report.**

---

## AICertify क्यों

अधिकांश AI-गवर्नेंस टूलिंग या तो:

- **एक वेंडर SaaS** है जो आपके ऑडिट ट्रेल को लॉगिन के पीछे बंद रखता है (Credo AI, Holistic AI), या
- **एक रिसर्च टूलकिट** है जो एक ही आयाम पर केंद्रित है: फेयरनेस मेट्रिक्स (Fairlearn, AI Fairness 360) या व्याख्यात्मकता (Microsoft RAI Toolbox)।

दोनों में से कोई भी वह डॉक्यूमेंट तैयार नहीं करता जिसकी रेगुलेटर वास्तव में मांग करता है: *प्रमाण कि आपने इस AI सिस्टम का परीक्षण एक नामित विनियमन के विरुद्ध किया है, पुनरुत्पादनीय पॉलिसीज़ और दिनांकित रिपोर्ट के साथ।*

AICertify उसी आर्टिफैक्ट के लिए बनाया गया है।

| | AICertify | Fairlearn / AIF360 | MS RAI Toolbox | Credo AI |
|---|---|---|---|---|
| ओपन सोर्स | ✅ Apache 2.0 | ✅ MIT | ✅ MIT | ❌ क्लोज़्ड |
| On-prem / air-gapped | ✅ | ✅ | ✅ | ❌ |
| नामित रेगुलेटरी फ्रेमवर्क्स | **EU AI Act, NIST RMF, Brazil AI Bill, India Digital Policy, +9 और** | ❌ (केवल फेयरनेस) | ❌ (टूलकिट) | ✅ |
| Policy-as-code (ऑडिटेबल, diff-able) | ✅ OPA / Rego | ❌ | ❌ | ❌ |
| बॉक्स से बाहर इंडस्ट्री वर्टिकल्स | Aviation, Banking, Healthcare, Automotive, Education | ❌ | ❌ | आंशिक |
| ऑडिट-तैयार रिपोर्ट्स जनरेट करता है | ✅ PDF / MD / JSON / HTML | ❌ | आंशिक | ✅ |
| कस्टम पॉलिसीज़ | ✅ एक `.rego` फ़ाइल ड्रॉप करें | ❌ | N/A | ✅ (पेड) |

---

## यह कैसे काम करता है

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram2_architecture_dark.svg">
    <img src="diagrams/diagram2_architecture_light.svg" alt="AICertify आर्किटेक्चर: आपका AI ऐप एक Contract को फीड करता है, जो Evaluators (Fairness, ContentSafety, RiskManagement, Compliance) के माध्यम से 85 Rego पॉलिसीज़ वाले OPA Engine में जाता है, और Report Generator के द्वारा एक ऑडिट डिलिवरेबल तैयार करता है" width="85%" />
  </picture>
</p>

1. **Contract**: आपके AI एप्लिकेशन का एक JSON विवरण: model, version, कैप्चर की गई interactions, metadata।
2. **Evaluators**: प्लग करने योग्य Python evaluators (Fairness, ContentSafety, RiskManagement, Compliance) आपकी interactions से मेट्रिक्स निकालते हैं।
3. **OPA policies**: मेट्रिक्स का मूल्यांकन विनियमन की Rego पॉलिसीज़ ([gopal](https://github.com/Principled-Evolution/gopal) पॉलिसी लाइब्रेरी से प्राप्त) के विरुद्ध किया जाता है।
4. **Report**: एक फॉर्मेटेड, दिनांकित आर्टिफैक्ट जिसे आप कानूनी टीम, ऑडिटर, या अपनी AI रिस्क कमेटी को सौंप सकते हैं।

चूंकि पॉलिसीज़ डिक्लेरेटिव Rego हैं, वे किसी भी अन्य कोड की तरह वर्ज़न, diff, और रिव्यू होती हैं। जब कोई विनियमन बदलता है, तो आप पॉलिसी अपडेट करते हैं, अपना मूल्यांकन हार्नेस नहीं।

---

## रेगुलेटरी कवरेज

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram3_regulatory_coverage_dark.svg">
    <img src="diagrams/diagram3_regulatory_coverage_light.svg" alt="रेगुलेटरी कवरेज: 8 फ्रेमवर्क्स और 5 इंडस्ट्रीज़ में 85 पॉलिसीज़ -- EU AI Act, NIST AI RMF, India Digital Policy, Brazil AI Bill, RTCA DO-365, FAA Part 107, EASA SORA, ICAO Doc 10019, Healthcare, Banking and Financial Services, Automotive, Education, Global, Aviation, AIOps, Corporate" width="85%" />
  </picture>
</p>

AICertify [gopal](https://github.com/Principled-Evolution/gopal) पॉलिसी लाइब्रेरी के विरुद्ध चलता है, जिसमें इन फ्रेमवर्क्स में **85 प्रोडक्शन OPA पॉलिसीज़** शामिल हैं:

### अंतर्राष्ट्रीय
- **EU AI Act** (29 पॉलिसीज़): निषिद्ध प्रथाएँ, बायोमेट्रिक ID, मैनिपुलेशन, पारदर्शिता, तकनीकी डॉक्यूमेंटेशन, मानवीय निगरानी, GPAI दायित्व। कई दायित्व क्षेत्र अभी पूर्ण कार्यान्वयन की प्रतीक्षा में scaffold हैं। आज वास्तव में कौन-से लागू करने योग्य हैं, यह जानने के लिए [gopal की coverage matrix](https://github.com/Principled-Evolution/gopal/blob/main/docs/coverage/eu-ai-act.md) देखें।
- **NIST AI RMF**: Govern, Map, Measure, Manage + AI 600-1
- **India Digital Policy**: NITI Aayog की National Strategy for Artificial Intelligence के अनुरूप (अलग से मौजूद India DPDP Act अभी कवर नहीं किया गया है)
- **Brazil AI Governance Bill**: एल्गोरिदमिक गवर्नेंस आवश्यकताएँ
- **एविएशन स्टैंडर्ड्स** (7 पॉलिसीज़): ICAO Doc 10019, FAA Part 107, FAA Remote ID, EASA Regulation 2019/947, EASA SORA, RTCA DO-365, ISO 21384

### इंडस्ट्री-विशिष्ट
- **Aviation** (12 पॉलिसीज़): एयरवर्थीनेस, ऑटोनॉमस सिस्टम्स, डेटा मैनेजमेंट, फ़्लाइट ऑपरेशंस
- **Education** (12 पॉलिसीज़): FERPA, COPPA, प्रॉक्टरिंग, human-in-the-loop ग्रेडिंग
- **Banking & Financial Services**: मॉडल रिस्क, fair lending
- **Healthcare**: पेशेंट सेफ्टी, डायग्नोस्टिक सेफ्टी
- **Automotive**: व्हीकल सेफ्टी इंटीग्रेशन

### Global & Operational
- **Global**: जवाबदेही, फेयरनेस, पारदर्शिता, व्याख्यात्मकता, कंटेंट सेफ्टी, रिस्क मैनेजमेंट, सिक्योरिटी
- **Corporate**: InfoSec, गवर्नेंस
- **AIOps & Cost**: स्केलेबिलिटी, संसाधन दक्षता

Global और Operational श्रेणियाँ अभी ज़्यादातर scaffold ही हैं (स्थिर package paths, पर अभी तक लागू करने योग्य लॉजिक नहीं)। प्रोडक्शन में किसी पॉलिसी पर भरोसा करने से पहले लिंक की गई coverage matrix या पॉलिसी की अपनी फ़ाइल ज़रूर जाँच लें।

अपना विनियमन यहाँ नहीं देखा? [एक Rego फ़ाइल जोड़ें](https://github.com/Principled-Evolution/gopal/blob/main/CONTRIBUTING.md)। लाइब्रेरी विस्तार के लिए डिज़ाइन की गई है।

---

## CLI

```bash
python -m aicertify.cli \
  --contract path/to/contract.json \
  --policy aicertify/opa_policies/international/eu_ai_act/v1 \
  --report-format pdf \
  --output-dir reports/
```

उपयोगी फ़्लैग्स:

| Flag | उद्देश्य |
|---|---|
| `--contract` | AI एप्लिकेशन कॉन्ट्रैक्ट JSON का पथ |
| `--policy` | जिसके विरुद्ध मूल्यांकन करना है उस OPA पॉलिसी फ़ोल्डर का पथ |
| `--report-format` | `pdf`, `markdown`, `json`, `html` (डिफ़ॉल्ट: `pdf`) |
| `--evaluators` | विशिष्ट evaluators तक सीमित करें (जैसे `Fairness ContentSafety`) |
| `--output-dir` | जहाँ रिपोर्ट्स लैंड होती हैं (डिफ़ॉल्ट: `./reports`) |
| `--verbose` | वर्बोज़ लॉगिंग |

पूर्ण Python API के लिए [`examples/quickstart.py`](examples/quickstart.py) देखें।

---

## आउटपुट देखें

यह देखने के लिए कि AICertify क्या तैयार करता है, आपको कुछ भी इंस्टॉल करने की ज़रूरत नहीं है। पहले से जनरेट की गई रिपोर्ट्स रीपो में कमिट की गई हैं:

- **[demo-report-eu-ai-act.pdf](docs/demo-report-eu-ai-act.pdf)**: EU AI Act के विरुद्ध मूल्यांकन किया गया एक customer-support agent
- [examples/outputs/eu_ai_act/](examples/outputs/eu_ai_act/): प्रामाणिक संपूर्ण आउटपुट
- [examples/outputs/loan_evaluation/](examples/outputs/loan_evaluation/): fair lending के लिए मूल्यांकन किया गया एक credit-scoring मॉडल
- [examples/outputs/medical_diagnosis/](examples/outputs/medical_diagnosis/): patient safety के लिए मूल्यांकन किया गया एक clinical-decision-support मॉडल

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram5_report_anatomy_dark.svg">
    <img src="diagrams/diagram5_report_anatomy_light.svg" alt="एक ऑडिट-तैयार रिपोर्ट की संरचना: फ्रेमवर्क नाम, एप्लिकेशन, मॉडल और दिनांक के साथ हेडर; executive summary; policy results table; risk assessment bar chart; remediation guidance; AICertify v0.8.0 का श्रेय देने वाला फुटर" width="85%" />
  </picture>
</p>

PDFs खोलिए। यही आपका ऑडिटर चाहता है।

---

## स्थिति

AICertify **beta (v0.8.0)** में है। 1.0 रिलीज़ से पहले API विकसित हो सकता है। आज प्रोडक्शन-तैयार फ्रेमवर्क्स:

- ✅ Global evaluators (fairness, content safety, transparency): सभी 9 पॉलिसीज़ लागू
- ✅ Aviation पॉलिसी सेट (ICAO, FAA, EASA, RTCA, ISO): सभी 19 पॉलिसीज़ लागू, अंतर्राष्ट्रीय रेगुलेटर्स और इंडस्ट्री वर्टिकल दोनों में
- ✅ Automotive: व्हीकल सेफ्टी पूरी तरह लागू
- 🚧 EU AI Act: 29 में से 8 पॉलिसीज़ लागू हैं, बाकी असली लॉजिक की प्रतीक्षा में scaffold हैं
- 🚧 NIST AI RMF: Govern और AI 600-1 orchestrator लागू हैं, Map, Measure, और Manage scaffold हैं
- 🚧 Healthcare, BFS: हर वर्टिकल में एक पॉलिसी लागू है (diagnostic safety, fair lending), दूसरी scaffold है (patient safety, model risk)
- 🚧 India Digital Policy: प्रारंभिक चरण

"scaffold" का मतलब है कि package path और default-deny संरचना मौजूद है, पर compliance लॉजिक अभी लिखा नहीं गया है, इसलिए वह हमेशा deny करता है। सटीक obligation-दर-obligation विवरण के लिए [gopal की coverage matrices](https://github.com/Principled-Evolution/gopal/tree/main/docs/coverage) देखें, और आगे क्या आ रहा है इसके लिए [पॉलिसी लाइब्रेरी रोडमैप](https://github.com/Principled-Evolution/gopal) देखें।

---

## OPA / Rego उपयोगकर्ताओं के लिए

यदि आप पहले से ही Kubernetes admission, माइक्रोसर्विस ऑथराइज़ेशन, या इंफ्रास्ट्रक्चर गवर्नेंस के लिए OPA का उपयोग करते हैं, तो AICertify आपकी मौजूदा पॉलिसी स्ट्रैटेजी में AI-सिस्टम स्लॉट है।

- **अपनी खुद की Rego पॉलिसीज़ लाएँ।** पॉलिसी फ़ोल्डर में एक `.rego` फ़ाइल ड्रॉप करें और वह बंडल्ड सेट के साथ मूल्यांकित होती है।
- **AI इंटरैक्शन्स का मूल्यांकन OPA के माध्यम से करें।** कैप्चर किए गए inputs, outputs, और metrics मानक OPA `input` डॉक्यूमेंट के ज़रिए आपकी पॉलिसीज़ में प्रवाहित होते हैं।
- **ऑडिट-तैयार एविडेंस जनरेट करें।** एक कमांड में PDF / Markdown / JSON / HTML।
- **अंतर्निहित पॉलिसी लाइब्रेरी के रूप में [gopal](https://github.com/Principled-Evolution/gopal) का उपयोग करें।** EU AI Act, NIST AI RMF, aviation safety, FERPA, fair lending, और अन्य को कवर करने वाली 85 प्रोडक्शन Rego पॉलिसीज़।

AICertify को [Open Policy Agent ecosystem](https://www.openpolicyagent.org/ecosystem/entry/principled-evolution) में Gopal के साथ AI-गवर्नेंस एंट्री के रूप में सूचीबद्ध किया गया है।

---

## AICertify क्यों?

अधिकांश AI गवर्नेंस प्रोग्राम PDFs, स्प्रेडशीट्स, और पॉलिसी डॉक्यूमेंट्स में सिमटे रहते हैं। वे बताते हैं कि क्या *होना चाहिए*, लेकिन यह सिद्ध नहीं करते कि क्या *हुआ*।

AICertify गवर्नेंस नियमों को निष्पादन योग्य पॉलिसी चेक्स में बदल देता है।

यह कहने के बजाय:

> "हमारा चैटबॉट हमारी responsible AI पॉलिसी का पालन करता है।"

आप यह प्रस्तुत कर सकते हैं:

> "यह रही कैप्चर की गई interaction, पॉलिसी वर्ज़न, OPA मूल्यांकन परिणाम, और जनरेट की गई ऑडिट रिपोर्ट।"

AICertify उन AI टीमों, गवर्नेंस टीमों, ऑडिटर्स, और प्लेटफ़ॉर्म इंजीनियरों के लिए है जिन्हें ऐसे AI कम्प्लायंस एविडेंस की ज़रूरत है जिसे **पढ़ा, चलाया, समीक्षित, और दोहराया जा सके**।

पूर्ण पोज़िशनिंग [docs/why-aicertify.md](docs/why-aicertify.md) में देखें।

---

## किसे योगदान करना चाहिए?

AICertify विशेष रूप से इनके लिए उपयोगी है:

- **AI इंजीनियर्स** जो रेगुलेटेड AI सिस्टम बना रहे हैं
- **Governance, risk, and compliance (GRC) टीमें** जो ऑडिट एविडेंस तैयार करती हैं
- **ऑडिटर्स और मॉडल रिस्क प्रोफेशनल्स** जो थर्ड-पार्टी AI का मूल्यांकन करते हैं
- **OPA / Rego उपयोगकर्ता** जिनकी रुचि AI-विशिष्ट पॉलिसी लेखन में है
- **Responsible AI शोधकर्ता** जिन्हें पुनरुत्पादनीय बेंचमार्क चाहिए
- **Python डेवलपर्स** जिनकी रुचि कम्प्लायंस ऑटोमेशन में है

**बिना-कोड योगदान का भी स्वागत है:** उदाहरण, पॉलिसी मैपिंग्स, डॉक्स, टेस्ट्स, रिपोर्ट टेम्पलेट्स, और रेगुलेटरी नोट्स।

शुरुआत करने के लिए [`good first issue`](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) और [`help wanted`](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) लेबल अच्छी जगह हैं।

---

## योगदान

हम स्वागत करते हैं:

- नए रेगुलेटरी फ्रेमवर्क्स (स्कोप संरेखित करने के लिए पहले एक issue खोलें)
- इंडस्ट्री-विशिष्ट पॉलिसीज़ जिन्हें आपने वास्तविक उपयोग में परखा है
- नए evaluators (fairness, safety, robustness, `aicertify/evaluators/` देखें)
- न्यूनतम पुनरुत्पादनीय कॉन्ट्रैक्ट के साथ बग रिपोर्ट्स
- डॉक्यूमेंटेशन, उदाहरण, और ट्यूटोरियल

[CONTRIBUTING.md](CONTRIBUTING.md), [Code of Conduct](CODE_OF_CONDUCT.md), और खुले [contributor issues](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) से शुरुआत करें।

सिक्योरिटी संबंधी समस्याओं के लिए कृपया [Security Policy](SECURITY.md) का पालन करें: सार्वजनिक issue के बजाय [security@principledevolution.ai](mailto:security@principledevolution.ai) पर निजी तौर पर रिपोर्ट करें।

---

## संबंधित प्रोजेक्ट्स

- **[gopal](https://github.com/Principled-Evolution/gopal)**: वह OPA पॉलिसी लाइब्रेरी जिसका AICertify उपयोग करता है। यदि आपको Python फ्रेमवर्क की आवश्यकता नहीं है तो OPA CLI के साथ स्टैंडअलोन उपयोग करें।
- **[Open Policy Agent](https://www.openpolicyagent.org/)**: पॉलिसी इंजन।
- **[Regal](https://github.com/StyraInc/regal)**: पॉलिसीज़ को साफ़ रखने के लिए उपयोग किया जाने वाला Rego linter।

---

## लाइसेंस

Apache License 2.0, [LICENSE](LICENSE) देखें।

---

<p align="center">
  <strong>⭐ यदि AICertify आपके लिए उपयोगी है, तो कृपया रीपो को स्टार करें और इसे किसी एक सहकर्मी के साथ साझा करें।</strong><br>
  <sub>हर स्टार AI गवर्नेंस और policy-as-code प्रैक्टिशनर्स को यह प्रोजेक्ट खोजने में मदद करता है।</sub>
</p>

<p align="center"><sub><a href="https://github.com/Principled-Evolution">Principled Evolution</a> द्वारा निर्मित · पॉलिसीज़ जिन्हें आप पढ़ सकते हैं, चला सकते हैं, और सिद्ध कर सकते हैं।</sub></p>
