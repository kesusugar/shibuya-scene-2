import {chromium} from 'playwright';
import {readFileSync,mkdirSync,existsSync} from 'node:fs';
const out='evidence/c2-nearby/boards';mkdirSync(out,{recursive:true});
const img=(path,label)=>`<section><h3>${label}</h3><img src="data:image/png;base64,${readFileSync(path).toString('base64')}"></section>`;
const b=await chromium.launch(),p=await b.newPage({viewport:{width:1560,height:800}});
for(const [id,view,year,caption] of [['shibuya109','b109','2019','円筒の白い外装・低層ガラス・自作近似の数字。屋根の元形状を保持。'],['mark-city','markcity','2025-06','東西の複合PLATEAUを1資産で表示。横帯と窓割りは推定。'],['hikarie','hikarie','2025-03','低層の金属小開口と上層ガラス。写真のカメラとは未校正。'],['stream','streamtower','2023-12','白い縦帯を追加。低層の緑化壁と2025年10月状態は未達。']]){
 const meta=JSON.parse(readFileSync(`assets/buildings/${id}/source/refs/reference.jpg.json`)),e=meta.imageinfo[0].extmetadata,credit=(e.Artist?.value??'').replace(/<[^>]+>/g,''),license=e.LicenseShortName?.value??'';
 await p.setContent(`<style>body{margin:0;background:#18212a;color:white;font:18px sans-serif}main{display:flex;gap:20px;padding:15px}h3{font-weight:normal}img{width:490px;height:650px;object-fit:contain}footer{padding:0 15px;line-height:1.5}</style><main>${img(`assets/buildings/${id}/source/refs/reference.jpg`,`参考写真 / ${year}`)}${img(`evidence/c2-nearby/before/${view}.png`,'追加前 / PR #34の状態')}${img(`evidence/c2-nearby/after/${view}.png`,'追加後 / 同じカメラ')}</main><footer>${caption}<br>画素誤差・実寸・広告・年代一致の合格ではありません。写真: ${credit} / ${license}。各資産のSOURCES.md参照。</footer>`);
 await p.screenshot({path:`${out}/${id}.png`});
}
for(const [view,label] of [['entry','初期画面・昼'],['entry_night','初期画面・夜']]){
 await p.setViewportSize({width:1260,height:640});await p.setContent(`<style>body{margin:0;background:#18212a;color:white;font:20px sans-serif}main{display:flex;gap:20px;padding:20px}img{width:600px;height:520px;object-fit:contain}</style><main>${img(`evidence/c2-nearby/before/${view}.png`,'追加前')}${img(`evidence/c2-nearby/after/${view}.png`,'追加後')}</main>${label}：q=low、SwiftShader。FPS評価ではありません。`);await p.screenshot({path:`${out}/${view}.png`});
}
await b.close();
