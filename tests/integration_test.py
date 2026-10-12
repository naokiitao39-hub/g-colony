import asyncio,time,json
from playwright.async_api import async_playwright
import sys
URL=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/g-colony/index.html'
async def ev(t,js,arg=None): return await asyncio.wait_for(t.evaluate(js,arg) if arg is not None else t.evaluate(js),10)
def ok(c,msg):
    print(('PASS ' if c else 'FAIL ')+msg,flush=True)
    if not c: ok.fails.append(msg)
ok.fails=[]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=2)
        pg=await ctx.new_page();errs=[]
        pg.on('pageerror',lambda e:errs.append('page:'+str(e)))
        pg.on('console',lambda m:errs.append('console:'+m.text) if m.type=='error' and 'ERR_' not in m.text and 'Failed to load' not in m.text else None)
        await pg.route('**/fonts.g*/**',lambda r:r.abort())
        await pg.goto(URL,wait_until='domcontentloaded');await asyncio.sleep(.8)
        # A/B locked
        ok(await ev(pg,"document.querySelector('#tGoki').classList.contains('locked')"),'初期状態でロック')
        await ev(pg,"document.querySelector('#tGoki').click()");await asyncio.sleep(.2)
        ok(not await ev(pg,"!!document.querySelector('#gokiFrame')") and await ev(pg,"!document.querySelector('#gokiNote').hidden"),'ロック中は入れずヒント表示')
        # C keys
        r=await ev(pg,"""(()=>{const {makeKey,readKey,decodePW,KANA}=window.__GC;let bad=0,n=0;for(let d=0;d<3;d++)for(const h of[0,1])for(let pop=0;pop<40000;pop+=1700){const k=makeKey(d,h,pop),o=readKey(k);n++;if(!o||o.diff!==d||o.haoh!==!!h||o.pop!==Math.min(31,Math.floor(pop/1000))*1000)bad++;let thr=false;try{decodePW(k)}catch(e){thr=true}if(!thr)bad+=1000;}
          let fp=0;for(let i=0;i<200000;i++){let s='';for(let j=0;j<5;j++)s+=KANA[Math.floor(Math.random()*32)];if(readKey(s))fp++;}return {n,bad,fp};})()""")
        ok(r['bad']==0,f"カギの往復と通常じゅもんとの非干渉 {r}");ok(r['fp']<200000*0.0005,f"でたらめ5文字の誤認率 {r['fp']}/200000")
        key=await ev(pg,"window.__GC.makeKey(2,1,23500)");print('key',key)
        # D unlock via load
        await ev(pg,"document.querySelector('#tLoad').click()");await asyncio.sleep(.2)
        await ev(pg,f"document.querySelector('#pwIn').value='{key}';document.querySelector('#lGo').click()");await asyncio.sleep(.3)
        ok(await ev(pg,"!document.querySelector('#tGoki').classList.contains('locked')&&!document.querySelector('#ovTitle').hidden"),'カギ入力で開放・タイトルへ')
        await pg.screenshot(path='m1_title_unlocked.png')
        # E open goki
        await ev(pg,"localStorage.setItem('gokitetsu-speed','2')")
        await ev(pg,"document.querySelector('#tGoki').click()");await asyncio.sleep(1.5)
        fr=pg.frame_locator('#gokiFrame');f=[x for x in pg.frames if x!=pg.main_frame][0]
        ok(await ev(f,"!document.querySelector('#ovTitle').hidden && document.querySelector('#movie').hidden"),'ゴキ鉄タイトル（オープニングなし）')
        ok(await ev(f,"JSON.stringify(window.__GCLEAR)")=='{"diff":2,"haoh":true,"pop":23000}','クリア情報の受け渡し')
        ok(await ev(f,"!document.querySelector('#tGC').hidden"),'G COLONYへ戻るボタン')
        await pg.screenshot(path='m2_goki_title.png')
        # F new game with bonus
        await ev(f,"document.querySelector('#tNew').click()");await asyncio.sleep(.3);await ev(f,"document.querySelector('#nGo').click()");await asyncio.sleep(.6)
        await ev(f,"const b=document.querySelector('#pFoot button');b&&b.click()");await asyncio.sleep(.4)
        for i in range(4):
            await ev(f,"document.querySelector('#msg').click()");await asyncio.sleep(.5)
        m=await ev(f,"[window.__GT.G.players[0].money,window.__GT.G.players[0].cards.join(',')]")
        ok(m[0]>5000 and '4' in m[1].split(','),f'クリア特典の付与 兵力={m[0]} カード={m[1]}')
        await ev(f,"window.__GT.G.auto=true;window.__GT.G.years=3;document.querySelector('#bDice').click()")
        t0=time.time();prog=[]
        while time.time()-t0<70:
            await ev(f,"""(()=>{const q=s=>document.querySelector(s);if(q('#fxov')&&!q('#fxov').hidden)q('#fxov').click();if(!q('#msg').hidden)q('#msg').click();if(!q('#panel').hidden){const b=[...document.querySelectorAll('#pFoot button')].pop();b&&b.click();}
              const d=q('#destBar');if(d&&!d.hidden){const b=d.querySelector('button.dest');b&&b.click();}})()""")
            await asyncio.sleep(.25)
            st=await ev(f,"[window.__GT.G.year,window.__GT.G.month]")
            if not prog or prog[-1]!=st:prog.append(st)
        print('進行',prog[:3],'...',prog[-1],'月数',len(prog))
        ok(len(prog)>=4,'自動プレイが進行する')
        await pg.screenshot(path='m3_goki_play.png')
        # G restart via title
        await ev(f,"window.parent.postMessage({gcolony:'restart'},'*')");await asyncio.sleep(1.2)
        f2=[x for x in pg.frames if x!=pg.main_frame][0]
        ok(await ev(f2,"!document.querySelector('#ovTitle').hidden"),'ゴキ鉄タイトルへ戻る（作り直し）')
        # H back to G COLONY
        await f2.evaluate("setTimeout(()=>document.querySelector('#tGC').click(),0)");await asyncio.sleep(.6)
        ok(await ev(pg,"!document.querySelector('#gokiFrame') && !document.querySelector('#ovTitle').hidden"),'G COLONYのタイトルへ戻る')
        # I G COLONY game & clear
        await ev(pg,"document.querySelector('#tNew').click()");await asyncio.sleep(.3)
        await ev(pg,"document.querySelector('#dEasy').click()");await asyncio.sleep(4)
        ok(await ev(pg,"['play','intro','swarm'].includes(window.__GC.mode)"),'G COLONYのゲーム開始 mode='+str(await ev(pg,"window.__GC.mode")))
        await ev(pg,"localStorage.removeItem('gcolony-key')")
        await ev(pg,"window.__GC.mode='play';window.__GC.G.diff=1;window.__GC.reachClear()");await asyncio.sleep(.4)
        k2=await ev(pg,"window.__GC.G.gokiKey");ok(bool(k2) and await ev(pg,f"localStorage.getItem('gcolony-key')==='{k2}'"),'クリアでカギ生成・保存 '+str(k2))
        await pg.screenshot(path='m4_clear.png')
        await ev(pg,"document.querySelector('#bClear').click()");await asyncio.sleep(24)
        ok(await ev(pg,"document.querySelector('#roll').innerHTML.includes('魔王城のカギ')"),'エンドロールにカギ')
        await asyncio.sleep(20);await pg.screenshot(path='m5_credits.png')
        ok(not errs,'エラーなし '+str(errs[:5]))
        # J fresh context, gokitetsu save unlock
        ctx2=await b.new_context(viewport={'width':1180,'height':820});pg2=await ctx2.new_page();e2=[];pg2.on('pageerror',lambda e:e2.append(str(e)))
        await pg2.route('**/fonts.g*/**',lambda r:r.abort())
        await pg2.goto(URL,wait_until='domcontentloaded');await asyncio.sleep(.6)
        ok(await ev(pg2,"document.querySelector('#tGoki').classList.contains('locked')"),'新しい端末ではロック')
        await ev(pg2,"localStorage.setItem('gokitetsu-save','x');window.__GC.updateGokiBtn()")
        ok(not await ev(pg2,"document.querySelector('#tGoki').classList.contains('locked')"),'ゴキ鉄のセーブがあれば開放')
        await ev(pg2,"document.querySelector('#tGoki').click()");await asyncio.sleep(1.5)
        f3=[x for x in pg2.frames if x!=pg2.main_frame][0]
        ok(await ev(f3,"window.__GCLEAR===null"),'カギなし開放では特典なし')
        await pg2.screenshot(path='m6_ipad_goki.png');ok(not e2,'iPadサイズでエラーなし '+str(e2[:3]))
        await b.close()
    print('FAILS',ok.fails)
asyncio.run(main())
