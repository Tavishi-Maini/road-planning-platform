import os
import gdown

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_FILES = {
    "total_cost_model.joblib": "https://drive.google.com/file/d/1AbKvOPEBzewgr4HrMcbjbiQyafzWxpGW/view?usp=sharing",
    "duration_model.joblib": "https://drive.google.com/file/d/1vUKAazUURVBvDtjP-CxFD4BubgzjTIe3/view?usp=sharing",
    "material_index_model.joblib": "https://drive.google.com/file/d/1V_vS_tTwa0XZK5Md5mFk9ItpvYTxOdDm/view?usp=sharing",
    "manpower_model.joblib": "https://drive.google.com/file/d/1Yy0CluU77r73n5VFnROgQJigSVjSFzyF/view?usp=drive_link",
    "machinery_model.joblib": "https://drive.google.com/file/d/1abOdpX3cqUaZCzO65letEVtMoXZMBq3E/view?usp=sharing",
}

def download_models():
    for filename, file_id in MODEL_FILES.items():
        path = os.path.join(MODEL_DIR, filename)

        if os.path.exists(path):
            print(f"Already exists: {filename}")
            continue

        url = f"https://drive.google.com/uc?id={file_id}"
        print(f"Downloading {filename}...")
        gdown.download(url, path, quiet=False)

if __name__ == "__main__":
    download_models()