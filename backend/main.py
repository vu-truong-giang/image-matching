from fastapi import FastAPI , UploadFile , File
from fastapi.middleware.cors import CORSMiddleware
from sift import extract_sift_features, match_images
import os 
import shutil
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