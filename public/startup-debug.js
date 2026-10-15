// Runs before the application module so initialization failures remain visible.
(() => {
  performance.setResourceTimingBufferSize(1000);
  const state = {phase:'JavaScriptを読み込み中',readyMs:null,firstFrameMs:null,errors:[],assets:[],marks:[],runtime:null};
  const now=()=>Math.round(performance.now());
  const panel=document.getElementById('debug-panel'),out=document.getElementById('debug-output'),button=document.getElementById('debug-toggle');
  const clean=value=>String(value).replace(/https?:\/\/[^\s"')]+/g, u=>{try{const x=new URL(u);return x.origin+x.pathname;}catch{return u;}}).slice(0,2000);
  function error(kind,value){state.errors.push({at:now(),kind,message:clean(value)});if(state.errors.length>100)state.errors.shift();button.textContent=`診断 (${state.errors.length})`;render();}
  function snapshot(){
    const resources=performance.getEntriesByType('resource');
    return {...state,elapsedMs:now(),page:location.origin+location.pathname,userAgent:navigator.userAgent,
      resources:resources.slice(-300).map(r=>({url:clean(r.name),durationMs:Math.round(r.duration),transferBytes:r.transferSize,decodedBytes:r.decodedBodySize})),
      transferBytes:resources.reduce((n,r)=>n+r.transferSize,0)};
  }
  function render(){
    if(panel.hidden)return;
    const s=snapshot(),done=s.assets.filter(a=>a.status!=='loading').length,failed=s.assets.filter(a=>a.status==='error').length;
    out.textContent=[`状態: ${s.phase}`,`ページ開始から: ${(s.elapsedMs/1000).toFixed(2)} 秒`,
      `街の準備完了: ${s.readyMs===null?'待機中':(s.readyMs/1000).toFixed(2)+' 秒'}`,
      `準備後の初回描画: ${s.firstFrameMs===null?'待機中':(s.firstFrameMs/1000).toFixed(2)+' 秒'}`,
      `資産処理: ${done}/${s.assets.length} 完了 / ${failed} 失敗（JSON解析・GLB展開を含む）`,
      `観測転送量: ${(s.transferBytes/1048576).toFixed(2)} MiB（キャッシュ等で0になる場合あり）`,
      s.runtime?`描画: ${JSON.stringify(s.runtime)}`:'',
      '\nエラー:',...s.errors.map(e=>`${(e.at/1000).toFixed(2)}s [${e.kind}] ${e.message}`),
      '\n処理時間の長い資産:',...s.assets.filter(a=>a.durationMs!==undefined).sort((a,b)=>b.durationMs-a.durationMs).slice(0,12).map(a=>`${(a.durationMs/1000).toFixed(2)}s ${a.status} ${a.url}`)].join('\n');
  }
  window.__startupDebug={state,error,mark(phase){state.phase=phase;state.marks.push({phase,at:now()});render();},
    begin(url){const a={url:clean(url),startMs:now(),status:'loading'};state.assets.push(a);return a;},
    end(a,failure){a.durationMs=now()-a.startMs;a.status=failure?'error':'ok';if(failure)error('asset',`${a.url}: ${failure}`);},
    ready(){state.readyMs=now();this.mark(state.errors.length?'一部エラーあり・表示を継続':'街の準備完了');},
    frame(runtime){state.runtime=runtime;if(state.readyMs!==null&&state.firstFrameMs===null)state.firstFrameMs=now();},snapshot};
  window.addEventListener('error',e=>{if(e instanceof ErrorEvent)error('JavaScript',e.message);else if(e.target?.src||e.target?.href)error('resource',e.target.src||e.target.href);},true);
  window.addEventListener('unhandledrejection',e=>error('Promise',e.reason?.message||e.reason));
  document.addEventListener('webglcontextlost',()=>{window.__startupDebug.mark('WebGLコンテキストを喪失');error('WebGL','描画を継続できません。再読み込みを試してください。');},true);
  button.onclick=()=>{panel.hidden=!panel.hidden;button.setAttribute('aria-expanded',String(!panel.hidden));render();};
  document.getElementById('debug-close').onclick=()=>{panel.hidden=true;button.setAttribute('aria-expanded','false');button.focus();};
  document.getElementById('debug-download').onclick=()=>{const u=URL.createObjectURL(new Blob([JSON.stringify(snapshot(),null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=u;a.download='shibuya-debug.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);};
  document.getElementById('debug-reload').onclick=()=>location.reload();
  const params=new URLSearchParams(location.search);
  if(params.has('debug')){panel.hidden=false;button.setAttribute('aria-expanded','true');}
  if(params.has('capture')){panel.hidden=true;button.hidden=true;}
  setInterval(render,500);render();
})();
