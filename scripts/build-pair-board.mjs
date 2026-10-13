import {chromium} from 'playwright';
import {readFileSync,mkdirSync} from 'node:fs';
import {dirname} from 'node:path';
const [before,after,out,label='同じ視点の前後比較']=process.argv.slice(2),uri=p=>'data:image/png;base64,'+readFileSync(p).toString('base64');mkdirSync(dirname(out),{recursive:true});
const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:1260,height:640},deviceScaleFactor:1});await page.setContent(`<style>body{margin:0;background:#18212a;color:#fff;font:20px sans-serif}main{display:flex;gap:20px;padding:20px}img{width:600px;height:520px;object-fit:contain}footer{font:17px sans-serif;padding:0 20px}</style><main><div>変更前<br><img src="${uri(before)}"></div><div>変更後<br><img src="${uri(after)}"></div></main><footer>${label}</footer>`);await page.screenshot({path:out});await browser.close();
