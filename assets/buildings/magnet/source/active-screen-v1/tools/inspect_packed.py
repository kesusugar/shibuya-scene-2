import bpy,json,hashlib,sys
from pathlib import Path
r=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(r/'output/magnet_screen_editable.blend'));assert not bpy.data.libraries
ims=[i for i in bpy.data.images if i.name not in {'Render Result','Viewer Node'}];assert len(ims)==5 and all(i.packed_file and len(i.pixels)>0 for i in ims)
out={'images':[{'name':i.name,'sha256':hashlib.sha256(bytes(i.packed_file.data)).hexdigest(),'bytes':len(i.packed_file.data)} for i in ims],'linked_libraries':0,'all_images_packed_readable':True,'read_only':True};(r/'reports/packed-reopen.json').write_text(json.dumps(out,indent=2))
