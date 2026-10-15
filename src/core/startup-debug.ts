export interface AssetTiming {url:string;startMs:number;status:string;durationMs?:number}
interface Diagnostics {
 error(kind:string,value:unknown):void;mark(phase:string):void;
 begin(url:string):AssetTiming;end(asset:AssetTiming,failure?:string):void;
 ready():void;frame(runtime:Record<string,unknown>):void;
}
declare global {interface Window {__startupDebug?:Diagnostics}}
export const debug=window.__startupDebug;
export async function measured<T>(url:string,load:()=>Promise<T>):Promise<T>{
 const asset=debug?.begin(url);
 try{const value=await load();if(asset)debug?.end(asset);return value;}
 catch(e){if(asset)debug?.end(asset,e instanceof Error?e.message:String(e));throw e;}
}
