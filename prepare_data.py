from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.datasets import load_iris, load_wine

DATA_DIR = Path("data")


def save_frame(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = frame.sort_values(list(frame.columns), kind="mergesort").reset_index(drop=True)
    ordered.to_csv(path, index=False, lineterminator="\n", float_format="%.10g")


def iris_frame() -> pd.DataFrame:
    return load_iris(as_frame=True).frame


def wine_frame() -> pd.DataFrame:
    return load_wine(as_frame=True).frame


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a deterministic dataset version")
    parser.add_argument("mode", choices=["base", "wine", "iris_features"])
    args = parser.parse_args()

    DATA_DIR.mkdir(exist_ok=True)
    iris_path = DATA_DIR / "iris.csv"
    wine_path = DATA_DIR / "wine.csv"

    if args.mode == "base":
        save_frame(iris_frame(), iris_path)
        wine_path.unlink(missing_ok=True)
    elif args.mode == "wine":
        save_frame(iris_frame(), iris_path)
        save_frame(wine_frame(), wine_path)
    else:
        frame = iris_frame()
        frame["sepal_area"] = frame["sepal length (cm)"] * frame["sepal width (cm)"]
        frame["petal_area"] = frame["petal length (cm)"] * frame["petal width (cm)"]
        save_frame(frame, iris_path)
        wine_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
