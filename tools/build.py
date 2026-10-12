#!/usr/bin/env python3
"""G COLONY のビルド。
src/gcolony.html（G COLONY本体）に src/goki.html（ゴキ鉄）を埋め込み、
  - index.html            … GitHub Pages / ホーム画面アプリ用（全画面設定・オフライン対応つき）
  - 引数で渡したパス     … Claudeのアーティファクト用（head無しの本体だけ）
を書き出す。使い方: python3 tools/build.py [アーティファクト用の出力先]
"""
import base64,sys,pathlib
R=pathlib.Path(__file__).resolve().parent.parent
src=(R/'src/gcolony.html').read_text()
goki=(R/'src/goki.html').read_text()
body=src.replace('__GOKI_B64__',base64.b64encode(goki.encode()).decode(),1)
assert '__GOKI_B64__' not in body
i=body.index('</style>')+len('</style>')
index=(R/'src/pwa-head.html').read_text()+body[:i].replace('<title>Gコロニー</title>','<title>G COLONY</title>',1)+'\n</head>\n<body>\n'+body[i:]+(R/'src/pwa-tail.html').read_text()
(R/'index.html').write_text(index)
if len(sys.argv)>1:pathlib.Path(sys.argv[1]).write_text(body)
print('index.html',len(index),'bytes')
