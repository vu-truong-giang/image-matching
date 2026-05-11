import cv2
import numpy as np
from watermark_dwt_svd import extract_watermark_dwt_svd

S_host = np.load("S_host.npy")
U_wm = np.load("U_wm.npy")
Vt_wm = np.load("Vt_wm.npy")

extracted = extract_watermark_dwt_svd(
    "watermarked.jpg",
    S_host,
    U_wm,
    Vt_wm,
    alpha=0.05
)

cv2.imwrite("extracted_watermark.jpg", extracted)

print("Đã trích watermark")