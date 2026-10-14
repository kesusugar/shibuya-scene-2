# 外側の点字警告面

元Core内で完全な警告面が置けなかった12端だけを対象に、Coreと追加PLATEAU歩道に照会。12端へ80枚を追加。元Core fillを測った交通面で補うことで12端とも完全な警告面を配置できた。元164枚、追加108枚、施設接続166枚は保持。位置・警告面と縁石の離隔・実際の誘導経路は推定。DEＭ補填や車道へは置かない。

Blender 4.2.3: source/blender/build.pyへlayout.json、Core crosswalks_measured.json、street_input.json、Core GLB、出力GLB、stats.json、西・中央・東の外側道路GLBを順に渡す。dot25個/guide4線の標準形。全突起頂点を歩道へ照会し、支柱・樹木・入口・柵を避ける。
