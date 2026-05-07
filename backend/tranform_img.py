from decode import decode
import cv2
import numpy as np


def rotate_image(img_path, angle=30):
    img = decode(img_path)
    if img is None:
        return None

    h, w = img.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, M, (w, h))


def crop_border(img_path, percent=0.1):
    img = decode(img_path)
    if img is None:
        return None

    h, w = img.shape[:2]

    crop_h = int(h * percent)
    crop_w = int(w * percent)

    return img[crop_h:h-crop_h, crop_w:w-crop_w]


def resize_image(img_path, scale=0.7):
    img = decode(img_path)
    if img is None:
        return None

    h, w = img.shape[:2]

    new_w = int(w * scale)
    new_h = int(h * scale)

    return cv2.resize(img, (new_w, new_h))


def change_brightness(img_path, beta=50):
    img = decode(img_path)
    if img is None:
        return None

    return cv2.convertScaleAbs(img, alpha=1, beta=beta)


def add_noise(img_path):
    img = decode(img_path)
    if img is None:
        return None

    noise = np.random.normal(0, 25, img.shape).astype(np.int16)
    noisy = img.astype(np.int16) + noise
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)

    return noisy