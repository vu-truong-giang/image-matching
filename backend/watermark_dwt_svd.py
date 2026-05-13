import cv2
import numpy as np
import pywt
import os

def find_uvs_files(image_filename , usv_dir):
    name = os.path.splitext(image_filename)[0]
   

    S_host_path = os.path.join(usv_dir, f"{name}_S_host.npy")
    U_wm_path = os.path.join(usv_dir, f"{name}_U_wm.npy")
    Vt_wm_path = os.path.join(usv_dir, f"{name}_Vt_wm.npy")

    return S_host_path, U_wm_path, Vt_wm_path


def read_gray_image(path, size=None):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise ValueError("Không đọc được ảnh")

    img = img.astype(np.float32)

    if size is not None:
        img = cv2.resize(img, size)

    return img


def embed_watermark_dwt_svd(host_path, watermark_path, alpha=0.05):
    """
    host_path: ảnh gốc
    watermark_path: ảnh watermark
    alpha: độ mạnh nhúng watermark
    """

    host = read_gray_image(host_path)

    # DWT ảnh gốc
    coeffs = pywt.dwt2(host, "haar")
    LL, (LH, HL, HH) = coeffs

    # Resize watermark bằng kích thước LL
    h, w = LL.shape
    watermark = read_gray_image(watermark_path, size=(w, h))

    # SVD LL và watermark
    U_host, S_host, Vt_host = np.linalg.svd(LL, full_matrices=False)
    U_wm, S_wm, Vt_wm = np.linalg.svd(watermark, full_matrices=False)

    # Nhúng watermark vào singular values
    S_new = S_host + alpha * S_wm

    # Tạo lại LL mới
    LL_new = np.dot(U_host, np.dot(np.diag(S_new), Vt_host))

    # IDWT để tạo ảnh đã nhúng
    watermarked = pywt.idwt2((LL_new, (LH, HL, HH)), "haar")

    watermarked = np.clip(watermarked, 0, 255).astype(np.uint8)

    return watermarked, S_host, U_wm, Vt_wm


def extract_watermark_dwt_svd(watermarked_path, S_host, U_wm, Vt_wm, alpha=0.05):
    """
    Trích watermark từ ảnh đã nhúng.
    Cần S_host, U_wm, Vt_wm đã lưu khi nhúng.
    """

    watermarked = read_gray_image(watermarked_path)

    coeffs = pywt.dwt2(watermarked, "haar")
    LL_w, (LH_w, HL_w, HH_w) = coeffs

    U_w, S_w, Vt_w = np.linalg.svd(LL_w, full_matrices=False)

    # Khôi phục singular values của watermark
    S_extract = (S_w - S_host) / alpha

    watermark_extract = np.dot(U_wm, np.dot(np.diag(S_extract), Vt_wm))

    watermark_extract = np.clip(watermark_extract, 0, 255).astype(np.uint8)

    return watermark_extract



