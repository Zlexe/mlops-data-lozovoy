from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from clearml import Dataset

PROJECT = "MIIT/MLOps/practice_3/lozovoy"
NAME = "sklearn-tabular-lozovoy"
DATA_DIR = Path("data")


def create_version(
    version: str,
    mode: str,
    description: str,
    parent_id: str | None = None,
    tags: list[str] | None = None,
) -> str:
    subprocess.run(["python", "prepare_data.py", mode], check=True)
    dataset = Dataset.create(
        dataset_project=PROJECT,
        dataset_name=NAME,
        dataset_version=version,
        description=description,
        parent_datasets=[parent_id] if parent_id else None,
    )
    dataset.sync_folder(local_path=str(DATA_DIR))
    if tags:
        dataset.add_tags(tags)
    dataset.upload()
    dataset.finalize()
    print(f"{version}: {dataset.id}")
    return dataset.id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="Create versions on ClearML")
    args = parser.parse_args()
    if not args.run:
        print("Dry run only. Add --run after clearml-init and server verification.")
        return

    base_id = create_version("1.0.0", "base", "Исходный Iris", tags=["base"])
    wine_id = create_version("1.1.0", "wine", "К базе добавлен Wine", parent_id=base_id)
    features_id = create_version(
        "2.0.0",
        "iris_features",
        "В Iris добавлены вычисляемые признаки",
        parent_id=base_id,
    )
    print(f"BASE_ID={base_id}")
    print(f"WINE_ID={wine_id}")
    print(f"IRIS_FEATURES_ID={features_id}")


if __name__ == "__main__":
    main()
