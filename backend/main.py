import cv2
from fastapi import FastAPI, Form , UploadFile , File
from fastapi.middleware.cors import CORSMiddleware
from sift import extract_sift_features, match_images
from tranform_img import rotate_image, crop_border, resize_image, change_brightness, add_noise
from watermark_dwt_svd import embed_watermark_dwt_svd, extract_watermark_dwt_svd , find_uvs_files
import os 
import shutil
import numpy as np
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response

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
    
app.mount("/dataset", StaticFiles(directory="dataset"), name="dataset")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/extracted", StaticFiles(directory=EXTRACT_DIR), name="extracted")
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
    attack_type: str = Form(...),
    value: float = Form(0)
):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location , "wb") as buffer:
        shutil.copyfileobj(file.file,buffer)
    if attack_type == "rotate":
        result = rotate_image(file_location, angle=value)

    elif attack_type == "crop":
            result = crop_border(file_location, percent=value)

    elif attack_type == "resize":
            result = resize_image(file_location, scale=value)

    elif attack_type == "brightness":
            result = change_brightness(file_location, beta=value)

    elif attack_type == "noise":
            result = add_noise(file_location)
    else:
        return {
            "message": "Invalid attack type"
        }
    output_filename = f"{attack_type}_{file.filename}"
    output_path = os.path.join(STATIC_DIR, output_filename)
    cv2.imwrite(output_path, result)
    return {
        "filename": file.filename,
        "attack_type": attack_type,
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



@app.post("/embed-watermark-folder")
async def embed_watermark_folder(
    files: list[UploadFile] = File(...),
    watermark: UploadFile = File(...)
):
    # lưu watermark
    watermark_location = os.path.join(
        WATERMARK_DIR,
        watermark.filename
    )
    with open(watermark_location, "wb") as buffer:
        shutil.copyfileobj(watermark.file, buffer)
    results = []
    for file in files:
        try:
            # lưu ảnh upload
            file_location = os.path.join(
                UPLOAD_DIR,
                file.filename
            )
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            # embed
            embedded_image, S_host, U_wm, Vt_wm = embed_watermark_dwt_svd(
                file_location,
                watermark_location,
                alpha=0.05
            )
            # tên output
            output_filename = f"watermarked_{file.filename}"
            output_path = os.path.join(
                DATASET_DIR,
                output_filename
            )

            cv2.imwrite(output_path, embedded_image)

            # lưu USV
            base_name = os.path.splitext(output_filename)[0]

            np.save(
                os.path.join(USV_DIR, f"{base_name}_S_host.npy"),
                S_host
            )

            np.save(
                os.path.join(USV_DIR, f"{base_name}_U_wm.npy"),
                U_wm
            )

            np.save(
                os.path.join(USV_DIR, f"{base_name}_Vt_wm.npy"),
                Vt_wm
            )

            os.remove(file_location)

            results.append({
                "filename": file.filename,
                "status": "success"
            })

        except Exception as e:

            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })

    return {
        "message": "Embed watermark completed",
        "total": len(files),
        "results": results
    }

@app.post("/extract-watermark")
async def extract_watermark(
    file: UploadFile = File(...),
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


@app.get("/dataset_png/{filename}")
def serve_dataset_png(filename: str):
    # Serve a TIFF file from DATASET_DIR converted to PNG on-the-fly
    file_path = os.path.join(DATASET_DIR, filename)
    if not os.path.exists(file_path):
        return {"message": "File not found"}

    img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return {"message": "Cannot read image (unsupported TIFF format)"}

    ok, buf = cv2.imencode('.png', img)
    if not ok:
        return {"message": "Failed to encode PNG"}

    return Response(content=buf.tobytes(), media_type="image/png")