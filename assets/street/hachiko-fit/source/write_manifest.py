import hashlib,json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
outputs={str(p.relative_to(root)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((root/'web').glob('*'))}
record={'asset':'hachiko-fit','datum_tp_m':15,'source_rights':'source/RIGHTS.md',
        'input_verification':'unchanged locally verified deliveries reused; no transfer/full ZIP revalidation',
        'verified_input_zip_sha256':{
          'a28_lottery_three_window_frontage_candidate_v002':'ff737e17f8afaa82375be08af25e80b04e727442753323e32d87163563e2d2e7',
          'a29_a8_entrance_shell_2025_v001':'14379f1cda3007f001caa6086c89224bedf20bd8d45d76b5bcd1db349b7f504a',
          'station_north_louver_frontage_v001_FRONT_ONLY':'b816e35e149af2a188bdd843e58761c4b5cd0857c14b5d7e051c64a4fcb86ecc',
          'hachiko_white_guardrail_detail_v001_PARTIAL':'4dceec3743ef66109aa0a385530b86768daf89d865f0e7bc6df838eff7b6e2b5'},
        'normal':['lottery','enclosure','finish','a8','louvre','fence','tactile','kerb'],'confirmation_preview':[],
        'outputs':outputs}
(root/'manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
