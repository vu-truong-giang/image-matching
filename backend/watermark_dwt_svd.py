import cv2
import numpy as np
import pywt
import os


def find_uvs_files(image_filename, usv_dir):
    name = os.path.splitext(image_filename)[0]

    S_host_path = os.path.join(usv_dir, f"{name}_S_host.npy")
    U_wm_path = os.path.join(usv_dir, f"{name}_U_wm.npy")
    Vt_wm_path = os.path.join(usv_dir, f"{name}_Vt_wm.npy")

    return S_host_path, U_wm_path, Vt_wm_path


def read_gray_image(path, size=None):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise ValueError(f"Không đọc được ảnh: {path}")

    if size is not None:
        img = cv2.resize(img, size)

    return img.astype(np.float32)


def embed_watermark_dwt_svd(host_path, watermark_path, alpha=0.05):
    # đọc ảnh màu
    host = cv2.imread(host_path, cv2.IMREAD_COLOR)

    if host is None:
        raise ValueError(f"Không đọc được ảnh gốc: {host_path}")

    # chuyển BGR sang YCrCb
    ycrcb = cv2.cvtColor(host, cv2.COLOR_BGR2YCrCb)

    y, cr, cb = cv2.split(ycrcb)

    y = y.astype(np.float32)

    # DWT trên kênh Y
    coeffs = pywt.dwt2(y, "haar")
    LL, (LH, HL, HH) = coeffs

    # watermark vẫn đọc xám
    h, w = LL.shape
    watermark = read_gray_image(watermark_path, size=(w, h))

    # SVD
    U_host, S_host, Vt_host = np.linalg.svd(
        LL,
        full_matrices=False
    )

    U_wm, S_wm, Vt_wm = np.linalg.svd(
        watermark,
        full_matrices=False
    )

    # nhúng
    S_new = S_host + alpha * S_wm

    LL_new = U_host @ np.diag(S_new) @ Vt_host

    # IDWT để khôi phục kênh Y
    watermarked_y = pywt.idwt2(
        (LL_new, (LH, HL, HH)),
        "haar"
    )

    watermarked_y = np.clip(
        watermarked_y,
        0,
        255
    ).astype(np.uint8)

    # xử lý nếu kích thước lệch 1 pixel do DWT
    watermarked_y = cv2.resize(
        watermarked_y,
        (ycrcb.shape[1], ycrcb.shape[0])
    )

    # ghép lại ảnh màu
    watermarked_ycrcb = cv2.merge([
        watermarked_y,
        cr,
        cb
    ])

    watermarked_bgr = cv2.cvtColor(
        watermarked_ycrcb,
        cv2.COLOR_YCrCb2BGR
    )

    return watermarked_bgr, S_host, U_wm, Vt_wm


def extract_watermark_dwt_svd(
    watermarked_path,
    S_host,
    U_wm,
    Vt_wm,
    alpha=0.05
):
    # đọc ảnh màu đã nhúng
    watermarked = cv2.imread(watermarked_path, cv2.IMREAD_COLOR)

    if watermarked is None:
        raise ValueError(f"Không đọc được ảnh watermarked: {watermarked_path}")

    # lấy kênh Y
    ycrcb = cv2.cvtColor(watermarked, cv2.COLOR_BGR2YCrCb)

    y, cr, cb = cv2.split(ycrcb)

    y = y.astype(np.float32)

    coeffs = pywt.dwt2(y, "haar")
    LL_w, (LH_w, HL_w, HH_w) = coeffs

    U_w, S_w, Vt_w = np.linalg.svd(
        LL_w,
        full_matrices=False
    )

    S_extract = (S_w - S_host) / alpha

    watermark_extract = U_wm @ np.diag(S_extract) @ Vt_wm

    watermark_extract = np.clip(
        watermark_extract,
        0,
        255
    ).astype(np.uint8)

    return watermark_extract