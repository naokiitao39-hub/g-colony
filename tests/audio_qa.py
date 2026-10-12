import asyncio,sys
from playwright.async_api import async_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/g-colony/index.html'
RMS="""(async(A)=>{if(!A||!A.ctx||!A.master)return -1;const an=A.ctx.createAnalyser();an.fftSize=2048;A.master.connect(an);const d=new Float32Array(2048);let s=0,n=0;const t0=performance.now();
  while(performance.now()-t0<1500){an.getFloatTimeDomainData(d);for(const v of d){s+=v*v;n++;}await new Promise(r=>setTimeout(r,50));}try{A.master.disconnect(an);}catch(e){}return Math.sqrt(s/n);})"""
fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m,flush=True)
    if not c:fails.append(m)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();ctx=await b.new_context(viewport={'width':1180,'height':820})
        await ctx.add_init_script("(()=>{const A=window.AudioContext;window.__acCount=0;window.AudioContext=function(...a){(window.top.__acTotal=(window.top.__acTotal||0)+1);return new A(...a)};window.AudioContext.prototype=A.prototype;})()")
        pg=await ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.route('**/fonts.g*/**',lambda r:r.abort())
        await pg.goto(URL,wait_until='domcontentloaded');await asyncio.sleep(.6)
        par=lambda: pg.evaluate("(()=>{const A=window.__GC.AU;return ("+RMS+")(A)})()")
        await pg.mouse.click(590,120);await asyncio.sleep(1)  # 本物のタップ
        ok(await par()>0.003,'A G COLONYのタイトルで曲が鳴る')
        await pg.evaluate("window.__GC.storeKey('つうへまこ')")
        await pg.click('#tGoki');await asyncio.sleep(2.2)
        f=[x for x in pg.frames if x!=pg.main_frame][0]
        gk=lambda: f.evaluate("(()=>{const A=window.__GT.AU;return ("+RMS+")(A)})()")
        ok(await par()<0.001,'B 魔王城に入るとG COLONYの曲は止まる')
        ok(await gk()>0.003,'B 魔王城に入った瞬間から（中をタップせずに）曲が鳴る')
        ok(await f.evaluate("window.__GT.AU.shared===true"),'B 音の部品を共有している')
        await f.click('.sndToggle');await asyncio.sleep(.4)
        ok(await gk()<0.001 and 'オフ' in await f.inner_text('.sndToggle'),'C 魔王城で音オフ→無音・表示オフ')
        await f.click('.sndToggle');await asyncio.sleep(.4)
        ok(await gk()>0.003 and 'オン' in await f.inner_text('.sndToggle'),'C 魔王城で音オン→鳴る・表示オン')
        await f.click('#tGC');await asyncio.sleep(1.2)
        ok(not await pg.evaluate("!!document.querySelector('#gokiFrame')"),'D G COLONYに戻ると魔王城の画面は消える')
        ok(await par()>0.003,'D 戻った瞬間からG COLONYの曲が鳴る（タップ不要）')
        # E: G COLONYで音オフ→魔王城
        await pg.click('#ovTitle .sndToggle');await asyncio.sleep(.4)
        ok(await par()<0.001,'E G COLONYで音オフ→無音')
        await pg.click('#tGoki');await asyncio.sleep(2.2);f=[x for x in pg.frames if x!=pg.main_frame][0]
        ok(await gk()<0.001 and 'オフ' in await f.inner_text('.sndToggle'),'E 音オフのまま魔王城→無音・表示オフ')
        await f.click('.sndToggle');await asyncio.sleep(.5)
        ok(await gk()>0.003,'E 魔王城で音オン→鳴る')
        await f.click('#tGC');await asyncio.sleep(1.2)
        ok(await par()>0.003 and 'オン' in await pg.inner_text('#ovTitle .sndToggle'),'E 戻るとG COLONYも音オン・鳴る')
        # F: 魔王城で音オフ→戻る
        await pg.click('#tGoki');await asyncio.sleep(2.2);f=[x for x in pg.frames if x!=pg.main_frame][0]
        await f.click('.sndToggle');await asyncio.sleep(.3)
        await f.click('#tGC');await asyncio.sleep(1.2)
        ok(await par()<0.001 and 'オフ' in await pg.inner_text('#ovTitle .sndToggle'),'F 魔王城で音オフ→戻るとG COLONYも無音・表示オフ')
        await pg.click('#ovTitle .sndToggle');await asyncio.sleep(.6)
        ok(await par()>0.003,'F G COLONYで音オン→鳴る')
        # G: 魔王城のタイトルへ（作り直し）を繰り返しても二重に鳴らない
        await pg.click('#tGoki');await asyncio.sleep(2)
        for i in range(3):
            f=[x for x in pg.frames if x!=pg.main_frame][0];await f.evaluate("window.parent.postMessage({gcolony:'restart'},'*')");await asyncio.sleep(1.8)
        f=[x for x in pg.frames if x!=pg.main_frame][0]
        r=await gk();ok(0.003<r<0.2,f'G 作り直しを3回しても1つ分だけ鳴る rms={r:.3f}')
        total=await pg.evaluate("window.__acTotal||0");ok(total==1,f'I 音の部品は全体で1つだけ（作られた数={total}）')
        # H: 一時停止→タップで復帰
        await pg.evaluate("window.__GC.AU.ctx.suspend()");await asyncio.sleep(.3)
        await f.click('#ovTitle',position={'x':50,'y':50});await asyncio.sleep(.6)
        ok(await pg.evaluate("window.__GC.AU.ctx.state")=='running','H 止まっていても魔王城の中のタップで復帰')
        # 効果音：サイコロ
        await f.click('#tNew');await asyncio.sleep(.3);await f.click('#nGo');await asyncio.sleep(.8)
        ok(not errs,'エラーなし '+str(errs[:3]))
        await b.close()
    print('FAILS',fails)
asyncio.run(main())
