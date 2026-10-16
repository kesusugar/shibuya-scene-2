"""Build the runtime derivative. Requires Pillow 12.3.0; never modifies the canonical scan.
Only JPEG resolution/encoding and descriptive material name change; geometry/UV/normal bytes stay exact.
"""
import hashlib,io,json,pathlib,struct
from PIL import Image
root=pathlib.Path(__file__).resolve().parents[2]
source=root/"source/scan-candidate/model/hachiko_uploaded_scan_candidate_v001.glb"
data=source.read_bytes()
assert hashlib.sha256(data).hexdigest()=="cd20601d57308a1b50892c05d509a6295ca24ca2045cfd37421995a840bf039e"
jl=struct.unpack_from("<I",data,12)[0]
doc=json.loads(data[20:20+jl]);binary=data[28+jl:]
image_view=doc["images"][0]["bufferView"]
view=doc["bufferViews"][image_view]
image=Image.open(io.BytesIO(binary[view.get("byteOffset",0):view.get("byteOffset",0)+view["byteLength"]])).convert("RGB")
image=image.resize((1536,1536),Image.Resampling.LANCZOS)
encoded=io.BytesIO();image.save(encoded,format="JPEG",quality=80,subsampling=2,optimize=False,progressive=False)
newbin=bytearray()
for idx,v in enumerate(doc["bufferViews"]):
 raw=binary[v.get("byteOffset",0):v.get("byteOffset",0)+v["byteLength"]]
 if idx==image_view:raw=encoded.getvalue()
 newbin.extend(b"\0"*((-len(newbin))%4));v["byteOffset"]=len(newbin);v["byteLength"]=len(raw);newbin.extend(raw)
doc["materials"][0]["name"]="street_hachiko_scan"
doc["asset"]["extras"]={"attribution":"Hachiko by Maurice Svay, CC BY 4.0","source":"https://sketchfab.com/3d-models/hachiko-fffee43c3cbc4b7ea20d6556a360b25f","runtime_change":"Embedded JPEG 4096 to 1536 px, Lanczos, JPEG quality 80, 4:2:0. Material name only changed for existing furniture look classification; material parameters unchanged."}
doc["buffers"][0]["byteLength"]=len(newbin)
newbin.extend(b"\0"*((-len(newbin))%4))
jb=json.dumps(doc,separators=(",",":"),ensure_ascii=True).encode();jb+=b" "*((-len(jb))%4)
out=struct.pack("<4sII",b"glTF",2,28+len(jb)+len(newbin))+struct.pack("<II",len(jb),0x4e4f534a)+jb+struct.pack("<II",len(newbin),0x004e4942)+newbin
assert len(out)<=3000000, f"Runtime asset over unchanged 3 MB budget: {len(out)}"
target=root/"web/hachiko.glb";target.write_bytes(out)
print(json.dumps({"runtimeBytes":len(out),"runtimeSha256":hashlib.sha256(out).hexdigest(),"textureBytes":len(encoded.getvalue()),"textureSize":[1536,1536]}))
