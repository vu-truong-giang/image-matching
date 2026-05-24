import cv2
import numpy as np


def resize_image(img, max_size=800):
    h, w = img.shape[:2]

    scale = max_size / max(h, w)

    if scale < 1:
        img = cv2.resize(
            img,
            (int(w * scale), int(h * scale))
        )

    return img


def decode(img_path):
    print("Đọc ảnh:", img_path)

    # đọc ảnh màu
    image = cv2.imread(
        img_path,
        cv2.IMREAD_COLOR
    )

    if image is None:
        print("Lỗi: Không đọc được ảnh")
        return None

    image = resize_image(image, 800)

    print("Shape:", image.shape)
    print("Dtype:", image.dtype)

    # ép uint8 nếu cần
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)

    return image