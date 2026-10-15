/** Resolve site-root assets under a static-host subdirectory; leave blob/data/external URLs intact. */
export function assetUrl(url:string,base=import.meta.env.BASE_URL):string {
 if(!url.startsWith('/')||url.startsWith('//')||url.startsWith(base))return url;
 return base.replace(/\/$/,'')+url;
}
