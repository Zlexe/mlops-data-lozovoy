from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd
from sklearn.datasets import load_iris, load_wine

DATA_DIR = Path("data")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_file(path: Path, expected_rows: int) -> pd.DataFrame:
    if not path.exists():
        raise AssertionError(f"Отсутствует ожидаемый файл: {path}")
    frame = pd.read_csv(path)
    if any(column.startswith("Unnamed:") for column in frame.columns):
        raise AssertionError(f"Найден безымянный индексный столбец в {path}")
    if len(frame) != expected_rows:
        raise AssertionError(f"Неверное число строк в {path}: {len(frame)}")
    if frame.isna().any().any():
        raise AssertionError(f"Найдены пропуски в {path}")
    print(f"{path}: sha256={sha256(path)}")
    print(f"  rows={len(frame)}, columns={len(frame.columns)}")
    print(f"  columns={list(frame.columns)}")
    print(f"  missing={int(frame.isna().sum().sum())}")
    return frame


def main() -> None:
    iris = check_file(DATA_DIR / "iris.csv", len(load_iris(as_frame=True).frame))
    wine_path = DATA_DIR / "wine.csv"
    if wine_path.exists():
        check_file(wine_path, len(load_wine(as_frame=True).frame))

    calculated = {"sepal_area", "petal_area"}
    if calculated.issubset(iris.columns):
        expected_sepal = iris["sepal length (cm)"] * iris["sepal width (cm)"]
        expected_petal = iris["petal length (cm)"] * iris["petal width (cm)"]
        if not iris["sepal_area"].eq(expected_sepal).all():
            raise AssertionError("Неверные значения sepal_area")
        if not iris["petal_area"].eq(expected_petal).all():
            raise AssertionError("Неверные значения petal_area")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, FileNotFoundError) as error:
        print(f"Проверка не пройдена: {error}", file=sys.stderr)
        raise SystemExit(1) from error
