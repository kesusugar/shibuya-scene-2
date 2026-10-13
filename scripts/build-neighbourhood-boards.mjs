import {chromium} from 'playwright';
import {readFileSync,mkdirSync} from 'node:fs';
const root=process.cwd()+'/',out=root+'evidence/c2-neighbourhood/boards';mkdirSync(out,{recursive:true});
const img=(p,t)=>`<div><h3>${t}</h3><img src="data:image/jpeg;base64,${readFileSync(root+p).toString('base64')}"></div>`;
const b=await chromium.launch(),page=await b.newPage({viewport:{width:1560,height:800}});
for(const [id,view,year,caption] of [['scramble-square','square','2023','縦桟と黒い縦帯を追加。屋根は元形状。屋上テラス・開口形の不足が残る。'],['fukuras','fukuras','2020','灰色の矩形腰壁とガラスを追加。低層の張り出し・開放バルコニーは未達。'],['quattro','center_front','2023','センター街の補助写真。個別建物の対応は未確認。窓割り・外装は推定。'],['center244','center244','2023','センター街の補助写真。個別建物の対応は未確認。窓割り・外装は推定。']]){
 const meta=JSON.parse(readFileSync(root+`assets/buildings/${id}/source/refs/reference.jpg.json`)),e=meta.imageinfo[0].extmetadata,credit=(e.Artist?.value??'').replace(/<[^>]+>/g,''),license=e.LicenseShortName?.value??'';
 await page.setContent(`<style>body{margin:0;background:#18212a;color:white;font:19px sans-serif}main{display:flex;gap:20px;padding:15px}h3{font-weight:normal;font-size:19px}img{width:490px;height:650px;object-fit:contain}footer{font-size:17px;padding:0 15px;line-height:1.5}</style><main>${img(`assets/buildings/${id}/source/refs/reference.jpg`,`写真 / ${year}年`)}${img(`evidence/c2-neighbourhood/before/${view}.png`,'追加前 / 同じカメラ')}${img(`evidence/c2-neighbourhood/after/${view}.png`,'追加後 / 同じカメラ')}</main><footer>${caption}<br>写真とのカメラは未校正。年代・広告・実寸の一致、画素誤差の合格を示す比較ではありません。写真: ${credit} / ${license}。出典: 各資産のSOURCES.md。</footer>`);
 await page.screenshot({path:`${out}/${id}.png`});
}await b.close();
