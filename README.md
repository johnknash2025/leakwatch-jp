# leakwatch-jp

自分のメールアドレスが過去の情報漏洩に含まれていないかを **公開API（標準は Have I Been Pwned）** で確認し、
深刻さの判定、対応手順の提案、進み具合の記録を **自分のPCの中だけで** 行うCLIです。

## できること
- 登録したメールアドレスを HIBP で確認する（`leakwatch check`）
- 漏洩した項目（パスワード、カード、電話番号など）から深刻さを判定する（低／中／高／緊急）
- 日本の主要サービスでの対応手順を表示する（`leakwatch guide`）
- 対応状況（未対応／対応済み）を記録・表示する（`leakwatch status` / `done`）
- 届いた「漏洩しました」メールの点検：偽ドメイン、急がせる表現、AIへの指示文の検出（`leakwatch mail`）
- 任意で、ローカルのOpenAI互換LLMによる補助判定（`--llm`）

## できないこと・しないこと
- **ダークウェブやTorを自前で巡回・スクレイピングすることはしません。漏洩データのダウンロードもしません。**
- パスワード変更、カード停止、各サービスへのログインは実行しません。**最後の操作はご本人が行います。**
- 銀行やカード会社の認証情報は扱いません。

### 自前でダークウェブを巡回しない理由
- 漏洩データを手元に持つと、それ自体が新たな漏洩リスクになり、法的にも問題になり得ます。
- 犯罪フォーラムに接続するとマルウェアや追跡の危険があります。
- HIBP のように、データを責任ある形で扱う専門サービスに任せたほうが正確で安全です。

## データの扱い
- 記録は `~/.leakwatch/state.json`（権限600）にだけ保存します。外部へ送るのは、確認に使うAPIへのメールアドレスだけです。
- APIキーは環境変数か macOS キーチェーンから読みます。表示・記録はしません。
- 暗号化保存は未対応です（今後の課題）。ディスク暗号化（FileVault など）を有効にしてください。
- LLMは `LEAKWATCH_LLM_URL` を設定したときだけ使います。ローカルのサーバーを推奨します。

## 使い方
```
pip install -e .
leakwatch add you@example.com
leakwatch check --source mock      # キーなしで動作確認（pwned@example.com が漏洩ありのモック）
leakwatch check                    # HIBP（要 HIBP_API_KEY）
leakwatch status
leakwatch done you@example.com:Adobe
leakwatch guide google
leakwatch mail suspicious.eml --llm
leakwatch sources
```

HIBP の APIキーはご自身で https://haveibeenpwned.com/API/Key から取得し、次のどちらかで設定してください。
- 環境変数 `HIBP_API_KEY`
- キーチェーン: `security add-generic-password -s leakwatch-jp -a HIBP_API_KEY -w`（実行すると入力を求められます）

ローカルLLM（例）: `LEAKWATCH_LLM_URL=http://127.0.0.1:18080/v1 LEAKWATCH_LLM_MODEL=glm-5.3-flash`

## 情報源の追加
`leakwatch/sources/` に `BreachSource` を実装して `REGISTRY` に登録します。SpyCloud や Flare は口だけ用意しています（未実装）。

## 対応手順データ
`leakwatch/data/playbooks.json`。リンクと電話番号は推測で書きません。確認できていないものは `verified: false` として表示時に「未確認」と出します。

## ライセンス
AGPL-3.0。AGPL の条件で使えない企業などには、別途商用ライセンスを相談で提供する予定です。
