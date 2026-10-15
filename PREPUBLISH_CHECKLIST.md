# 公開前チェック（本人確認用）
- [ ] README の「できること／できないこと」に誤りや言い過ぎがない
- [ ] playbooks.json のリンクを公式サイトで1件ずつ確認し、正しければ `verified: true` と確認日を付ける
- [ ] カード会社・証券会社の窓口を収録するなら、公式ページで確認したものだけにする
- [ ] HIBP の利用規約（商用利用・表示義務 "Powered by HIBP"）を確認し、README に記載する
- [ ] ライセンス（AGPL-3.0＋商用ライセンス）でよいか。外部の貢献を受けるなら CLA を用意する
- [ ] 本物の HIBP キーで `leakwatch check` を1回試す（キーはご本人が入力）
- [ ] git 履歴に個人情報やキーが入っていない（`git log -p | grep -i key` など）
- [ ] GitHub の Private vulnerability reporting を有効にする
- [ ] 上記が済んだら「公開して」と伝える
