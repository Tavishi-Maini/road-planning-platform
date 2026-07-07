import joblib
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "models" / "total_cost_model.joblib"


def inspect_model():
    model = joblib.load(MODEL_PATH)

    print("\nMODEL TYPE:", type(model))

    if hasattr(model, "steps"):
        print("\nPipeline steps:")
        for name, step in model.steps:
            print(name, "->", type(step))

    for name, step in model.steps:
        if isinstance(step, ColumnTransformer):
            print("\nColumnTransformer found:", name)

            for transformer_name, transformer, columns in step.transformers_:
                print("\nTransformer:", transformer_name)
                print("Type:", type(transformer))
                print("Columns:", columns)

                if isinstance(transformer, OneHotEncoder):
                    print("OneHotEncoder categories:")
                    for col, cats in zip(columns, transformer.categories_):
                        print(col, "=>", cats, "types:", {type(x) for x in cats})


if __name__ == "__main__":
    inspect_model()