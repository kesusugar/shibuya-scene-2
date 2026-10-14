import {chromium} from 'playwright';
import {mkdirSync,readFileSync,copyFileSync,writeFileSync} from 'node:fs';
const out='evidence/c2-exterior/boards';mkdirSync(out,{recursive:true});
const baseline=process.argv[2] ?? 'evidence/c2-nearby/after/';
// Reuse the parent's settled initial views: same pose and q=low.
const log=JSON.parse(readFileSync('evidence/c2-exterior/before/capture_log.json'));
const prior=JSON.parse(readFileSync(baseline+'capture_log.json'));
for(const v of ['entry','entry_night']){copyFileSync(baseline+v+'.png',`evidence/c2-exterior/before/${v}.png`);log[v]={...prior[v],copiedFrom:'PR #35 evidence/c2-nearby/after'};}
writeFileSync('evidence/c2-exterior/before/capture_log.json',JSON.stringify(log,null,2)+'\n');
const uri=path=>'data:image/png;base64,'+readFileSync(path).toString('base64');
const b=await chromium.launch(),p=await b.newPage({viewport:{width:1260,height:680}});
for(const [v,caption] of [['exterior_walk','109前：仮fillから車道・歩道・縁石へ。元の測ったCore地面は保持。'],['exterior_markcity','マークシティ側：追加PLATEAU道路と推定縁石。'],['terrain','駅周辺：道路の上にDEMを重ねず、元の屋根・上面を保持して足元を接続。'],['entry','初期画面・昼：既存の交差点と高度な街路設備を保持。'],['entry_night','初期画面・夜：点灯・光量・写真の年代一致は未達。']]){
 await p.setContent(`<style>body{margin:0;background:#18212a;color:white;font:20px sans-serif}main{display:flex;gap:20px;padding:20px}img{width:600px;height:520px;object-fit:contain}footer{padding:0 20px;font-size:18px;line-height:1.5}</style><main><div>追加前<br><img src="${uri(`evidence/c2-exterior/before/${v}.png`)}"></div><div>追加後<br><img src="${uri(`evidence/c2-exterior/after/${v}.png`)}"></div></main><footer>${caption}<br>同じカメラ・q=low/SwiftShader。標高欠測・縁石・点字の位置は推定。実機FPS・写真の画素誤差の合格ではありません。</footer>`);await p.screenshot({path:`${out}/${v}.png`});
}
await b.close();
