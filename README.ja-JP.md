<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/hero_banner_dark.svg">
    <img src="diagrams/hero_banner_light.svg" alt="AICertify — Compliance-as-code for AI systems" width="100%">
  </picture>
</div>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <strong>日本語</strong> |
  <a href="README.ko-KR.md">한국어</a> |
  <a href="README.hi-IN.md">हिन्दी</a>
</p>

<p align="center">
  <em>EU AI Act、NIST AI RMF をはじめとする 15 のフレームワークに対して、AI を監査する。契約 1 つ、コマンド 1 つ、レポート 1 つで完結します。</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/aicertify/"><img src="https://img.shields.io/pypi/v/aicertify?style=flat-square&color=blue" alt="PyPI"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml"><img src="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/stargazers"><img src="https://img.shields.io/github/stars/Principled-Evolution/aicertify?style=flat-square" alt="Stars"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12%2B-blue.svg?style=flat-square" alt="Python 3.12+"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square" alt="Apache 2.0"></a>
  <a href="https://www.openpolicyagent.org/"><img src="https://img.shields.io/badge/built%20on-OPA-7D4698.svg?style=flat-square" alt="Built on OPA"></a>
  <a href="https://github.com/Principled-Evolution/gopal"><img src="https://img.shields.io/badge/policies-94%20rego-2f9e44.svg?style=flat-square" alt="94 Rego Policies"></a>
  <a href="https://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome"></a>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram1_hero_flow_dark.svg">
    <img src="diagrams/diagram1_hero_flow_light.svg" alt="AI アプリケーションから監査対応レポートまで: AI アプリケーション → AICertify 契約 → OPA ポリシー評価 → コンプライアンスレポート" width="85%" />
  </picture>
</p>

<br>

規制当局は、社内のガバナンス文書よりも速いペースで動いています。EU AI Act はすでに発効済み、NIST AI RMF は米国における事実上の標準であり、インド、ブラジル、シンガポールが次に続きます。`AICertify` は、こうした義務を実行可能な [Open Policy Agent](https://www.openpolicyagent.org/) ポリシーとして表現し、収集した AI とのやり取りに対して評価を実行し、PDF、Markdown、JSON、HTML 形式の監査対応レポートを生成します。

「責任ある AI のポリシーがあります」と「それを証明できます」の間にあった、欠けていた橋渡しです。

---

## クイックスタート

```bash
pip install aicertify
```

同梱のデモを実行するには(サンプル契約と examples 一式を取得するためにリポジトリをクローンします):

```bash
git clone https://github.com/Principled-Evolution/aicertify.git
cd aicertify
python examples/quickstart.py
```

クイックスタートでは、サンプル AI アプリケーションを EU AI Act のポリシーセットに通し、コンプライアンスレポートを `reports/` に出力します。それを開いてみてください。手書きではなく、生成された監査成果物の実例です。

### 開発用のセットアップ

```bash
git clone https://github.com/Principled-Evolution/aicertify.git
cd aicertify
pip install -e .
```

### 最小限の Python での使い方

```python
from aicertify import regulations, application

# 1. 認証対象としたい規制を選択
regs = regulations.create("my_regulations")
regs.add("eu_ai_act")

# 2. AI アプリケーションをラップ
app = application.create(
    name="customer-support-bot",
    model_name="gpt-4o",
    model_version="2024-08-06",
)

# 3. 実際のやり取りを投入
app.add_interaction(
    input_text="I want a refund for my order",
    output_text="I can help with that. Could you share your order number?",
)

# 4. 評価を実行してレポートを取得
await app.evaluate(regulations=regs, report_format="pdf", output_dir="reports")
```

これがループの全体像です。**契約 → インタラクション → 評価 → レポート。**

---

## AICertify が選ばれる理由

既存の AI ガバナンスツールの多くは、次のいずれかに該当します。

- **ベンダー SaaS**: 監査ログがログイン画面の奥に閉じ込められている (Credo AI、Holistic AI)、または
- **研究用ツールキット**: 公平性指標 (Fairlearn、AI Fairness 360) や説明可能性 (Microsoft RAI Toolbox) など、単一の側面のみに特化している。

どちらも、規制当局が実際に求める文書、すなわち *「名前の付いた規制に対してこの AI システムをテストし、再現可能なポリシーと日付入りのレポートで裏付けた証拠」* を生み出しません。

AICertify はまさにその成果物のために構築されています。

| | AICertify | Fairlearn / AIF360 | MS RAI Toolbox | Credo AI |
|---|---|---|---|---|
| オープンソース | ✅ Apache 2.0 | ✅ MIT | ✅ MIT | ❌ クローズド |
| オンプレミス / エアギャップ環境 | ✅ | ✅ | ✅ | ❌ |
| 名前の付いた規制フレームワーク | **EU AI Act、NIST RMF、ブラジル AI 法案、インド DPDP ほか 11 件** | ❌ (公平性のみ) | ❌ (ツールキット) | ✅ |
| ポリシー・アズ・コード (監査・差分比較可) | ✅ OPA / Rego | ❌ | ❌ | ❌ |
| 業種別ポリシー標準装備 | 航空、銀行、医療、自動車、教育 | ❌ | ❌ | 部分対応 |
| 監査対応レポートの生成 | ✅ PDF / MD / JSON / HTML | ❌ | 部分対応 | ✅ |
| カスタムポリシー | ✅ `.rego` ファイルを配置するだけ | ❌ | 該当なし | ✅ (有償) |

---

## 仕組み

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram2_architecture_dark.svg">
    <img src="diagrams/diagram2_architecture_light.svg" alt="AICertify のアーキテクチャ: AI アプリが契約を生成し、評価器 (公平性、コンテンツ安全性、リスク管理、コンプライアンス) を経由して 94 個の Rego ポリシーを持つ OPA エンジンに送られ、レポート生成器が監査成果物を出力" width="85%" />
  </picture>
</p>

1. **契約 (Contract)** — AI アプリケーションを記述した JSON です。モデル、バージョン、収集したやり取り、メタデータを含みます。
2. **評価器 (Evaluators)** — プラガブルな Python 評価器 (公平性、コンテンツ安全性、リスク管理、コンプライアンス) が、やり取りからメトリクスを抽出します。
3. **OPA ポリシー** — 抽出されたメトリクスは、規制ごとの Rego ポリシー ([gopal](https://github.com/Principled-Evolution/gopal) ポリシーライブラリ由来) に対して評価されます。
4. **レポート** — 日付入りのフォーマット済み成果物として、法務、監査人、AI リスク委員会へ提出できます。

ポリシーは宣言的な Rego で書かれているため、他のコードと同じくバージョン管理、差分比較、レビューが可能です。規制が変わったら、評価ハーネスではなくポリシーを更新するだけで済みます。

---

## 規制カバレッジ

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram3_regulatory_coverage_dark.svg">
    <img src="diagrams/diagram3_regulatory_coverage_light.svg" alt="規制カバレッジ: 15 以上のフレームワークと 5 つの業種にわたる 94 ポリシー -- EU AI Act、NIST AI RMF、インド DPDP、ブラジル AI 法案、RTCA DO-365/366、FAA Part 107、EASA SORA、ICAO Doc 10019、医療、銀行・金融サービス、自動車、教育、グローバル、航空、AIOps、コーポレート" width="85%" />
  </picture>
</p>

AICertify は [gopal](https://github.com/Principled-Evolution/gopal) ポリシーライブラリ — **本番運用可能な 94 個の OPA ポリシー** — を用いて、以下のフレームワークに対する評価を実行します。

### 国際フレームワーク
- **EU AI Act** — 29 ポリシー。禁止行為、生体識別、操作 (manipulation)、透明性、技術文書、人間による監督、GPAI 義務をカバー
- **NIST AI RMF** — Govern、Map、Measure、Manage に加え AI 600-1
- **インド Digital Policy** — DPDP に整合する義務
- **ブラジル AI ガバナンス法案** — アルゴリズム・ガバナンス要件
- **航空標準** — ICAO Doc 10019、RTCA DO-365/366、ASTM F3442、ISO 21384、FAA Part 107、EASA SORA

### 業種別
- **航空** (17 ポリシー) — Detect-and-Avoid、認証、設計、統合検証
- **教育** (12 ポリシー) — FERPA、COPPA、試験監督、ヒューマン・イン・ザ・ループでの採点
- **銀行・金融サービス** — モデルリスク、公正融資
- **医療** — 患者安全、診断安全
- **自動車** — 車両安全統合

### グローバル & オペレーショナル
- **グローバル** — アカウンタビリティ、公平性、透明性、説明可能性、コンテンツ安全性、リスク管理、セキュリティ
- **コーポレート** — 情報セキュリティ、ガバナンス
- **AIOps & コスト** — スケーラビリティ、リソース効率

該当する規制が見当たらない場合は [Rego ファイルを追加](https://github.com/Principled-Evolution/gopal/blob/main/CONTRIBUTING.md) してください。ライブラリは拡張可能な設計になっています。

---

## CLI

```bash
python -m aicertify.cli \
  --contract path/to/contract.json \
  --policy aicertify/opa_policies/international/eu_ai_act/v1 \
  --report-format pdf \
  --output-dir reports/
```

主なフラグ:

| フラグ | 用途 |
|---|---|
| `--contract` | AI アプリケーション契約 JSON のパス |
| `--policy` | 評価対象とする OPA ポリシーフォルダのパス |
| `--report-format` | `pdf`、`markdown`、`json`、`html` (デフォルト: `pdf`) |
| `--evaluators` | 特定の評価器に限定 (例: `Fairness ContentSafety`) |
| `--output-dir` | レポート出力先 (デフォルト: `./reports`) |
| `--verbose` | 詳細ログ出力 |

Python API の全体像は [`examples/quickstart.py`](examples/quickstart.py) を参照してください。

---

## サンプルレポート

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram5_report_anatomy_dark.svg">
    <img src="diagrams/diagram5_report_anatomy_light.svg" alt="監査対応レポートの構成: フレームワーク名・アプリケーション・モデル・日付を含むヘッダー、エグゼクティブサマリー、ポリシー結果テーブル、リスク評価の棒グラフ、是正ガイダンス、AICertify v0.7.0 を示すフッター" width="85%" />
  </picture>
</p>

`examples/outputs/` ディレクトリには、実評価から生成されたレポートが含まれており、実行前に内容を確認できます。

- `eu_ai_act/` — EU AI Act に対して評価したカスタマーサポートエージェント
- `loan_evaluation/` — 公正融資の観点で評価した信用スコアリングモデル
- `medical_diagnosis/` — 患者安全の観点で評価した臨床意思決定支援モデル

PDF を開いてみてください。監査人が求めているのは、まさにこの形式の文書です。

---

## ステータス

AICertify は現在 **ベータ版 (v0.7.0)** です。1.0 リリースまでに API が変更される可能性があります。本日時点で本番運用可能なフレームワークは次のとおりです。

- ✅ EU AI Act
- ✅ グローバル評価器 (公平性、コンテンツ安全性、透明性)
- ✅ 医療、BFS、自動車の業種別ポリシー
- ✅ 航空ポリシーセット (RTCA、ASTM、FAA、EASA)
- 🚧 NIST AI RMF — 部分対応
- 🚧 インド Digital Policy — 初期段階

進捗状況は [ポリシーライブラリのロードマップ](https://github.com/Principled-Evolution/gopal) で確認できます。

---

## コントリビューション

以下のような貢献を歓迎しています。

- 新しい規制フレームワーク (スコープのすり合わせのため、まず issue を立ててください)
- 実運用で鍛え上げた業種別ポリシー
- 新しい評価器 (公平性、安全性、堅牢性 — `aicertify/evaluators/` を参照)
- 最小限の再現用契約を添えたバグレポート

まずは [CONTRIBUTING.md](CONTRIBUTING.md) と [行動規範](CODE_OF_CONDUCT.md) をご確認ください。

---

## 関連プロジェクト

- **[gopal](https://github.com/Principled-Evolution/gopal)** — AICertify が内部で使用している OPA ポリシーライブラリです。Python フレームワークが不要な場合は、OPA CLI と組み合わせて単体で利用できます。
- **[Open Policy Agent](https://www.openpolicyagent.org/)** — ポリシーエンジン本体。
- **[Regal](https://github.com/StyraInc/regal)** — ポリシーを清潔に保つために使用している Rego リンター。

---

## ライセンス

Apache License 2.0 — [LICENSE](LICENSE) を参照してください。

<p align="center"><sub>Built by <a href="https://github.com/Principled-Evolution">Principled Evolution</a> · 読める、動かせる、証明できるポリシー。</sub></p>
