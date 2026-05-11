import cv2
import numpy as np
from watermark_dwt_svd import embed_watermark_dwt_svd, extract_watermark_dwt_svd

host_path = "backend/dataset/22828930_15.tiff"
watermark_path = "backend/dataset/watermark.jpg"

print(host_path)
print(watermark_path)

watermarked, S_host, U_wm, Vt_wm = embed_watermark_dwt_svd(
    host_path,
    watermark_path,
    alpha=0.05
)

cv2.imwrite("watermarked.jpg", watermarked)

np.save("S_host.npy", S_host)
np.save("U_wm.npy", U_wm)
np.save("Vt_wm.npy", Vt_wm)

print("Đã nhúng watermark")