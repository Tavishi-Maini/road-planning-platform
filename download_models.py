import os
import gdown

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_FILES = {
    "total_cost_model.joblib": "1AbKvOPEBzewgr4HrMcbjbiQyafzWxpGW",
    "duration_model.joblib": "1vUKAazUURVBvDtjP-CxFD4BubgzjTIe3",
    "material_index_model.joblib": "1V_vS_tTwa0XZK5Md5mFk9ItpvYTxOdDm",
    "manpower_model.joblib": "1Yy0CluU77r73n5VFnROgQJigSVjSFzyF",
    "machinery_model.joblib": "1abOdpX3cqUaZCzO65letEVtMoXZMBq3E",
}

def download_models():
    for filename, file_id in MODEL_FILES.items():
        path = os.path.join(MODEL_DIR, filename)

        if os.path.exists(path):
            print(f"Already exists: {filename}")
            continue

        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        print(f"Downloading {filename}...")
        gdown.download(url, path, quiet=False)

if __name__ == "__main__":
    download_models()