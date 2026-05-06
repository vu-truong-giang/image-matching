import cv2
import numpy as np

def resize_image(img, max_size=800):
    h, w = img.shape[:2]
    scale = max_size / max(h, w)

    if scale < 1:
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    return img
def extract_sift_features(image_path):

    print("Đọc ảnh:", image_path)

    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)



    # Kiểm tra đọc ảnh
    if image is None:
        print("Lỗi: Không đọc được ảnh")
        return None, None

    image = resize_image(image, 800)
    print("Shape:", image.shape)
    print("Dtype:", image.dtype)

    # Chuyển về uint8 nếu cần
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)

    sift = cv2.SIFT_create(nfeatures=1000)

    keypoints, descriptors = sift.detectAndCompute(image, None)

    return keypoints, descriptors

def match_images(query_des, train_des):
    if query_des is None or train_des is None:
        return 0

    bf = cv2.BFMatcher()

    matches = bf.knnMatch(query_des, train_des, k=2)

    good_matches = []

    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    return len(good_matches)