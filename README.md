# G COLONY

家屋侵略シミュレーション「G COLONY」と、クリア後に遊べる「ゴキ鉄 魔王城建国記」。

- 遊ぶ：https://naokiitao39-hub.github.io/g-colony/
- iPhone / iPad：Safariで開いて「共有 → ホーム画面に追加」すると、金色のGのアイコンから全画面で起動できます。一度開けば電波がなくても遊べます。
- セーブは「ふっかつのじゅもん」方式です。

## 開発メモ

- `src/gcolony.html` … G COLONY本体（`__GOKI_B64__` の位置にゴキ鉄が埋め込まれる）
- `src/goki.html` … ゴキ鉄 魔王城建国記
- `src/pwa-head.html` / `src/pwa-tail.html` … ホーム画面アプリ用の設定とオフライン対応の読み込み
- `python3 tools/build.py [アーティファクト用の出力先]` … `index.html` を作り直す
- `tests/integration_test.py` / `tests/audio_qa.py` … Playwrightによる通しテストと音のQA
- 音は G COLONY 側の AudioContext を1つだけ作り、ゴキ鉄（iframe）もそれを共有する。ミュートは音量だけで行い、画面を離れたときの停止・再開は G COLONY 側がまとめて管理する。
- ゲームを更新したら `sw.js` の `VERSION` を上げる。
