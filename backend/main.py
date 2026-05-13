import cv2
from fastapi import FastAPI, Form , UploadFile , File
from fastapi.middleware.cors import CORSMiddleware
from sift import extract_sift_features, match_images
from tranform_img import rotate_image, crop_border, resize_image, change_brightness, add_noise
from watermark_dwt_svd import embed_watermark_dwt_svd, extract_watermark_dwt_svd , find_uvs_files
import os 
import shutil
import numpy as np
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173" , "http://localhost:5173"], #frontend url 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
DATASET_DIR = "dataset"
os.makedirs(DATASET_DIR, exist_ok=True)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)
WATERMARK_DIR = "watermarks"
os.makedirs(WATERMARK_DIR, exist_ok=True)
USV_DIR = "usv"
os.makedirs(USV_DIR, exist_ok=True)
EXTRACT_DIR = "extracted"
os.makedirs(EXTRACT_DIR, exist_ok=True)
@app.get("/")
def read_root():
    return {"message": "Backend is running 🚀"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {
        "filename": file.filename,
        "path": file_location,
        "message": "File uploaded successfully"
    }
@app.post("/sift-info")
async def sift_info(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    keypoints, descriptors = extract_sift_features(file_location)
    
    return {
        "filename": file.filename,
        "num_keypoints": len(keypoints),
        "descriptor_shape": descriptors.shape if descriptors is not None else None,
        "message": "SIFT features extracted successfully"
    }
@app.post("/search")
async def search_similar_image(file: UploadFile = File(...)):
    query_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(query_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    query_kp, query_des = extract_sift_features(query_path)

    if query_des is None:
        return {
            "message": "Cannot extract features from query image"
        }

    results = []

    for image_name in os.listdir(DATASET_DIR):
        image_path = os.path.join(DATASET_DIR, image_name)

        train_kp, train_des = extract_sift_features(image_path)

        score = match_images(query_des, train_des)

        results.append({
            "image_name": image_name,
            "score": score
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return {
        "query_image": file.filename,
        "results": results[:5]
    }
@app.post("/transform")
async def transform_image(
    file: UploadFile = File(...),
    transform_type: str = Form(...),
    angle: float = Form(30),
    percent: float = Form(0.1),
    scale: float = Form(0.7),
    beta: float = Form(50)
):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location , "wb") as buffer:
        shutil.copyfileobj(file.file,buffer)
    if transform_type == "rotate":
        transformed = rotate_image(file_location, angle)
    elif transform_type == "crop":
        transformed = crop_border(file_location, percent)
    elif transform_type == "resize":
        transformed = resize_image(file_location, scale)
    elif transform_type == "brightness":
        transformed = change_brightness(file_location, beta)
    elif transform_type == "noise":
        transformed = add_noise(file_location)
    else:
        return {
            "message": "Invalid transform type"
        }
    output_filename = f"{transform_type}_{file.filename}"
    output_path = os.path.join(STATIC_DIR, output_filename)
    cv2.imwrite(output_path, transformed)
    return {
        "filename": file.filename,
        "transform_type": transform_type,
        "output_path": output_path,
        "message": "Image transformed successfully"
    }

@app.post("/embed-watermark")
async def embed_watermark(
    file: UploadFile = File(...),
    watermark: UploadFile = File(...)
):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    watermark_location = os.path.join(WATERMARK_DIR, watermark.filename)
    with open(watermark_location, "wb") as buffer:
        shutil.copyfileobj(watermark.file, buffer)

    embedded_image , S_host, U_wm, Vt_wm = embed_watermark_dwt_svd(file_location, watermark_location , alpha=0.05)

    output_filename = f"watermarked_{file.filename}"
    output_path = os.path.join(DATASET_DIR, output_filename)
    cv2.imwrite(output_path, embedded_image)

    originnal_output_filename = os.path.splitext(output_filename)[0]
    np.save(f"{USV_DIR}/{originnal_output_filename}_S_host.npy", S_host)
    np.save(f"{USV_DIR}/{originnal_output_filename}_U_wm.npy", U_wm)
    np.save(f"{USV_DIR}/{originnal_output_filename}_Vt_wm.npy", Vt_wm)


    os.remove(file_location)

    return {
        "filename": file.filename,
        "output_path": output_path,
        "message": "Watermark embedded successfully"
    }

@app.post("/extract-watermark")
async def extract_watermark(
    file: UploadFile = File(...),
    S_host: UploadFile = File(...),
    U_wm: UploadFile = File(...),
    Vt_wm: UploadFile = File(...)
):
    file_location = os.path.join(STATIC_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    S_host_location , U_wm_location , Vt_wm_location = find_uvs_files(file.filename , USV_DIR)
            
    extracted_watermark = extract_watermark_dwt_svd(
                            file_location,
                            np.load(S_host_location),
                            np.load(U_wm_location), 
                            np.load(Vt_wm_location),
                            alpha=0.05
                        )
    
    output_filename = f"extracted_{file.filename}"
    output_path = os.path.join(EXTRACT_DIR, output_filename)
    cv2.imwrite(output_path, extracted_watermark)

    return {
        "filename": file.filename,
        "output_path": output_path,
        "message": "Watermark extracted successfully"
    }