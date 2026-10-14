"""Regenerate ONLY January CC0 blade crops from the committed WB01 target crop.
Python3 + Pillow. No view-only/copyrighted reference is read or copied.
"""
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]/'refs'
im=Image.open(R/'WB01-target-2025-01.png')
for i,quad in enumerate([(211,573,219,834,249,831,238,576),(269,696,278,958,306,949,297,695)]):
 im.transform((96,960),Image.Transform.QUAD,quad,Image.Resampling.BICUBIC).save(R/f'blade-{i+1}-2025-01.png')
