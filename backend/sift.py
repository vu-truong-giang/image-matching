from decode import decode
import cv2
import numpy as np


def extract_sift_features(image_path):

    image = decode(image_path)

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