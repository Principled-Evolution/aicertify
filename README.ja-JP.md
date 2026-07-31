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
  <em>EU AI Act、NIST AI RMF に加え、さらに 6 つの国際的なフレームワークに対して AI を監査する。契約 1 つ、コマンド 1 つ、レポート 1 つで完結します。</em>
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
    <img src="diagrams/diagram1_hero_flow_light.svg" alt="AI アプリケーションから監査対応レポートまで: AI アプリケーション → AICertify 契約 → OPA ポリシー評価 → コンプライアンスレポート" width="85%" />
  </picture>
</p>

<br>

規制当局は、社内のガバナンス文書よりも速いペースで動いています。EU AI Act はすでに発効済み、NIST AI RMF は米国における事実上の標準であり、インド、ブラジル、シンガポールが次に続きます。`AICertify` は、こうした義務を実行可能な [Open Policy Agent](https://www.openpolicyagent.org/) ポリシーとして表現し、収集した AI とのやり取りに対して評価を実行し、PDF、Markdown、JSON、HTML 形式の監査対応レポートを生成します。

「責任ある AI のポリシーがあります」と「それを証明できます」の間にあった、欠けていた橋渡しです。

**次のような場面で活用できます。**

- AI ガバナンスポリシーを実行可能なチェックに変換する
- リリースのたびに監査対応可能なコンプライアンス証跡を生成する
- 名前の付いた規制フレームワーク(EU AI Act、NIST AI RMF、FERPA、公正融資、FAA/EASA 航空関連など)に対して AI とのやり取りを評価する
- 監査人が読める Markdown、JSON、HTML、PDF レポートを生成する
- AI コンプライアンスチェックを CI/CD に組み込む

AICertify は [Open Policy Agent エコシステム](https://www.openpolicyagent.org/ecosystem/entry/principled-evolution) の一員であり、Kubernetes のアドミッション制御やマイクロサービスの認可、大規模なインフラガバナンスを支えているのと同じポリシーエンジンの上に構築されています。

> ⭐ **AICertify が役に立ったら、ぜひリポジトリにスターをお願いします。** AI ガバナンスやポリシー・アズ・コードに取り組む方々がこのプロジェクトを見つける助けになります。

---

## クイックスタート

```bash
# 1. AICertify をインストール(初回は約 3〜5 分。langchain と transformers を取得します)
pip install aicertify

# 2. OPA バイナリを一度だけインストール(約 80 MB)
curl -L https://openpolicyagent.org/downloads/latest/opa_linux_amd64 -o /usr/local/bin/opa && sudo chmod +x /usr/local/bin/opa

# 3. 同梱のデモを実行(契約ファイル不要、API キー不要、約 10 秒)
aicertify demo
```

`aicertify demo` は同梱のサンプル契約を読み込み、OPA 経由で EU AI Act のポリシーセットに対して評価を行い、`aicertify_demo_report.md` をカレントディレクトリに書き出します。レポートを開いてみてください。それが監査成果物の実例です。

<p align="center">
  <img src="docs/demo.gif" alt="aicertify demo の実行録画: バナー、スピナー、評価の進行状況、生成されたレポートのパス" width="85%" />
</p>

より高度な評価(LangFair の公平性メトリクス、DeepEval によるコンテンツ安全性スコアリング、PDF レポート)については、[`examples/quickstart.py`](examples/quickstart.py) と [フォーク可能なサンプルボット](examples/) を参照してください。各サンプルには `input_contract.json`、`policy_config.yaml`、`run.py` が同梱されています。

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
| 名前の付いた規制フレームワーク | **EU AI Act、NIST RMF、ブラジル AI 法案、インド Digital Policy ほか 9 件** | ❌ (公平性のみ) | ❌ (ツールキット) | ✅ |
| ポリシー・アズ・コード (監査・差分比較可) | ✅ OPA / Rego | ❌ | ❌ | ❌ |
| 業種別ポリシー標準装備 | 航空、銀行、医療、自動車、教育 | ❌ | ❌ | 部分対応 |
| 監査対応レポートの生成 | ✅ PDF / MD / JSON / HTML | ❌ | 部分対応 | ✅ |
| カスタムポリシー | ✅ `.rego` ファイルを配置するだけ | ❌ | 該当なし | ✅ (有償) |

---

## 仕組み

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram2_architecture_dark.svg">
    <img src="diagrams/diagram2_architecture_light.svg" alt="AICertify のアーキテクチャ: AI アプリが契約を生成し、評価器 (公平性、コンテンツ安全性、リスク管理、コンプライアンス) を経由して 85 個の Rego ポリシーを持つ OPA エンジンに送られ、レポート生成器が監査成果物を出力" width="85%" />
  </picture>
</p>

1. **契約 (Contract)**: AI アプリケーションを記述した JSON です。モデル、バージョン、収集したやり取り、メタデータを含みます。
2. **評価器 (Evaluators)**: プラガブルな Python 評価器 (公平性、コンテンツ安全性、リスク管理、コンプライアンス) が、やり取りからメトリクスを抽出します。
3. **OPA ポリシー**: 抽出されたメトリクスは、規制ごとの Rego ポリシー ([gopal](https://github.com/Principled-Evolution/gopal) ポリシーライブラリ由来) に対して評価されます。
4. **レポート**: 日付入りのフォーマット済み成果物として、法務、監査人、AI リスク委員会へ提出できます。

ポリシーは宣言的な Rego で書かれているため、他のコードと同じくバージョン管理、差分比較、レビューが可能です。規制が変わったら、評価ハーネスではなくポリシーを更新するだけで済みます。

---

## 規制カバレッジ

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram3_regulatory_coverage_dark.svg">
    <img src="diagrams/diagram3_regulatory_coverage_light.svg" alt="規制カバレッジ: 8 つのフレームワークと 5 つの業種にわたる 85 ポリシー -- EU AI Act、NIST AI RMF、インド Digital Policy、ブラジル AI 法案、RTCA DO-365、FAA Part 107、EASA SORA、ICAO Doc 10019、医療、銀行・金融サービス、自動車、教育、グローバル、航空、AIOps、コーポレート" width="85%" />
  </picture>
</p>

AICertify は [gopal](https://github.com/Principled-Evolution/gopal) ポリシーライブラリ(本番運用可能な 85 個の OPA ポリシー)を用いて、以下のフレームワークに対する評価を実行します。

### 国際フレームワーク
- **EU AI Act** (29 ポリシー): 禁止行為、生体識別、操作(manipulation)、透明性、技術文書、人間による監督、GPAI 義務をカバー。いくつかの義務領域は本格実装待ちのスキャフォールドであり、現時点でどれが実際に強制力を持つかは [gopal のカバレッジマトリクス](https://github.com/Principled-Evolution/gopal/blob/main/docs/coverage/eu-ai-act.md) を参照してください。
- **NIST AI RMF**: Govern、Map、Measure、Manage に加え AI 600-1
- **インド Digital Policy**: NITI Aayog の国家人工知能戦略(National Strategy for Artificial Intelligence)に整合したもの(別建てのインド DPDP 法はまだ対象外です)
- **ブラジル AI ガバナンス法案**: アルゴリズム・ガバナンス要件
- **航空標準** (7 ポリシー): ICAO Doc 10019、FAA Part 107、FAA Remote ID、EASA Regulation 2019/947、EASA SORA、RTCA DO-365、ISO 21384

### 業種別
- **航空** (12 ポリシー): 耐空性、自律システム、データ管理、運航
- **教育** (12 ポリシー): FERPA、COPPA、試験監督、ヒューマン・イン・ザ・ループでの採点
- **銀行・金融サービス**: モデルリスク、公正融資
- **医療**: 患者安全、診断安全
- **自動車**: 車両安全統合

### グローバル & オペレーショナル
- **グローバル**: アカウンタビリティ、公平性、透明性、説明可能性、コンテンツ安全性、リスク管理、セキュリティ
- **コーポレート**: 情報セキュリティ、ガバナンス
- **AIOps & コスト**: スケーラビリティ、リソース効率

グローバルおよびオペレーショナルのカテゴリーは、現時点ではスキャフォールド(パッケージパスは確定しているものの、強制力のあるロジックはまだ実装されていない状態)であることの方が多いです。本番環境で利用する前に、リンク先のカバレッジマトリクスまたはポリシー自体のファイルを確認してください。

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

何もインストールしなくても、AICertify が生成する成果物を確認できます。事前生成済みのレポートがリポジトリにコミットされています。

- **[demo-report-eu-ai-act.pdf](docs/demo-report-eu-ai-act.pdf)**: EU AI Act に対して評価したカスタマーサポートエージェント
- [examples/outputs/eu_ai_act/](examples/outputs/eu_ai_act/): 完全な出力の代表例
- [examples/outputs/loan_evaluation/](examples/outputs/loan_evaluation/): 公正融資の観点で評価した信用スコアリングモデル
- [examples/outputs/medical_diagnosis/](examples/outputs/medical_diagnosis/): 患者安全の観点で評価した臨床意思決定支援モデル

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram5_report_anatomy_dark.svg">
    <img src="diagrams/diagram5_report_anatomy_light.svg" alt="監査対応レポートの構成: フレームワーク名・アプリケーション・モデル・日付を含むヘッダー、エグゼクティブサマリー、ポリシー結果テーブル、リスク評価の棒グラフ、是正ガイダンス、AICertify v0.7.3 を示すフッター" width="85%" />
  </picture>
</p>

PDF を開いてみてください。監査人が求めているのは、まさにこの形式の文書です。

---

## ステータス

AICertify は現在 **ベータ版 (v0.7.3)** です。1.0 リリースまでに API が変更される可能性があります。本日時点で本番運用可能なフレームワークは次のとおりです。

- ✅ グローバル評価器(公平性、コンテンツ安全性、透明性): 9 ポリシーすべてを実装済み
- ✅ 航空ポリシーセット(ICAO、FAA、EASA、RTCA、ISO): 国際規制と業種別の両方を合わせた 19 ポリシーすべてを実装済み
- ✅ 自動車: 車両安全を完全実装済み
- 🚧 EU AI Act: 29 ポリシー中 8 ポリシーを実装済み。残りは本格実装待ちのスキャフォールド
- 🚧 NIST AI RMF: Govern と AI 600-1 オーケストレーターは実装済み。Map、Measure、Manage はスキャフォールド
- 🚧 医療、BFS: 各業種で 1 ポリシーずつ実装済み(診断安全性、公正融資)。もう一方はスキャフォールド(患者安全、モデルリスク)
- 🚧 インド Digital Policy: 初期段階

「スキャフォールド」とは、パッケージパスとデフォルト拒否の構造は存在するものの、コンプライアンスロジックがまだ実装されておらず、常に拒否 (deny) される状態を指します。義務項目ごとの詳細な内訳は [gopal のカバレッジマトリクス](https://github.com/Principled-Evolution/gopal/tree/main/docs/coverage) を、今後の予定は [ポリシーライブラリのロードマップ](https://github.com/Principled-Evolution/gopal) を参照してください。

---

## OPA / Rego ユーザーの方へ

すでに Kubernetes のアドミッション制御やマイクロサービスの認可、インフラガバナンスに OPA を使っているなら、AICertify は既存のポリシー戦略における「AI システム」の枠を埋める存在です。

- **自前の Rego ポリシーを持ち込める。** ポリシーフォルダに `.rego` ファイルを配置するだけで、同梱のポリシーセットと並んで評価されます。
- **OPA を通じて AI とのやり取りを評価できる。** 収集された入力・出力・メトリクスは、標準の OPA `input` ドキュメントを介してポリシーに渡されます。
- **監査対応の証跡を生成できる。** PDF / Markdown / JSON / HTML を、コマンド 1 つで。
- **[gopal](https://github.com/Principled-Evolution/gopal) を土台のポリシーライブラリとして利用できる。** EU AI Act、NIST AI RMF、航空安全、FERPA、公正融資などをカバーする 85 個の本番運用可能な Rego ポリシーです。

AICertify は [Open Policy Agent エコシステム](https://www.openpolicyagent.org/ecosystem/entry/principled-evolution) に、Gopal と並ぶ AI ガバナンス領域のエントリとして掲載されています。

---

## なぜ AICertify なのか

多くの AI ガバナンスの取り組みは、PDF やスプレッドシート、ポリシー文書の中で完結しています。そこに書かれているのは「本来こうあるべきだ」という姿であり、「実際にそうだった」という証明ではありません。

AICertify は、ガバナンスのルールを実行可能なポリシーチェックへと変換します。

次のように言うのではなく。

> 「当社のチャットボットは、責任ある AI ポリシーに従っています」

次のように示せます。

> 「これが記録されたやり取りであり、ポリシーのバージョンであり、OPA による評価結果であり、生成された監査レポートです」

AICertify は、**読める・動かせる・レビューできる・繰り返せる** AI コンプライアンス証跡を必要とする AI チーム、ガバナンスチーム、監査人、プラットフォームエンジニアのためのものです。

詳しいポジショニングは [docs/why-aicertify.md](docs/why-aicertify.md) を参照してください。

---

## 貢献に向いている人

AICertify は、特に次のような方に役立ちます。

- 規制対象の AI システムを構築する **AI エンジニア**
- 監査証跡を作成する **ガバナンス・リスク・コンプライアンス (GRC) チーム**
- サードパーティの AI を評価する **監査人やモデルリスクの専門家**
- AI 特有のポリシー記述に関心のある **OPA / Rego ユーザー**
- 再現可能なベンチマークを求める **責任ある AI の研究者**
- コンプライアンス自動化に関心のある **Python 開発者**

**コード以外の貢献も歓迎します。** サンプル、ポリシーのマッピング、ドキュメント、テスト、レポートテンプレート、規制に関するノートなど。

まずは [`good first issue`](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) や [`help wanted`](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) ラベルの付いた issue から見てみてください。

---

## コントリビューション

以下のような貢献を歓迎しています。

- 新しい規制フレームワーク (スコープのすり合わせのため、まず issue を立ててください)
- 実運用で鍛え上げた業種別ポリシー
- 新しい評価器 (公平性、安全性、堅牢性。詳細は `aicertify/evaluators/` を参照)
- 最小限の再現用契約を添えたバグレポート
- ドキュメント、サンプル、チュートリアル

まずは [CONTRIBUTING.md](CONTRIBUTING.md)、[行動規範](CODE_OF_CONDUCT.md)、そして募集中の [コントリビューター向け issue](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) をご確認ください。

セキュリティに関する問題は、公開の issue ではなく [Security Policy](SECURITY.md) に従って [security@principledevolution.ai](mailto:security@principledevolution.ai) まで非公開でご報告ください。

---

## 関連プロジェクト

- **[gopal](https://github.com/Principled-Evolution/gopal)**: AICertify が内部で使用している OPA ポリシーライブラリです。Python フレームワークが不要な場合は、OPA CLI と組み合わせて単体で利用できます。
- **[Open Policy Agent](https://www.openpolicyagent.org/)**: ポリシーエンジン本体。
- **[Regal](https://github.com/StyraInc/regal)**: ポリシーを清潔に保つために使用している Rego リンター。

---

## ライセンス

Apache License 2.0。詳細は [LICENSE](LICENSE) をご覧ください。

---

<p align="center">
  <strong>⭐ AICertify が役に立ったら、ぜひリポジトリにスターを付けて、同僚 1 人にシェアしてください。</strong><br>
  <sub>スターの一つひとつが、AI ガバナンスやポリシー・アズ・コードに取り組む人たちがこのプロジェクトを見つける助けになります。</sub>
</p>

<p align="center"><sub>Built by <a href="https://github.com/Principled-Evolution">Principled Evolution</a> · 読める、動かせる、証明できるポリシー。</sub></p>
