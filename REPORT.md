# Отчёт по практике 3: версионирование данных с DVC и ClearML

## 1. Окружение

- ОС: macOS
- Python: 3.12.14
- DVC: 3.67.1
- ClearML SDK: 2.1.12
- pandas: 3.1.0
- scikit-learn: 1.9.1
- Git branch: `main`

Зависимости зафиксированы в `requirements.txt`, `pyproject.toml` и `poetry.lock`.

## 2. Подготовка данных

Скрипт `prepare_data.py` поддерживает три режима:

- `base`: создаёт исходный `data/iris.csv`;
- `wine`: создаёт Iris и добавляет `data/wine.csv`;
- `iris_features`: добавляет к Iris `sepal_area` и `petal_area` и удаляет Wine.

CSV сохраняются без индекса, после детерминированной сортировки и с одинаковыми параметрами сериализации.

`check_data.py` проверяет наличие файлов, число строк и столбцов, названия столбцов, пропуски, SHA-256 и формулы вычисляемых признаков.

## 3. DVC

Базовый Git commit:

```text
5f665e03acc52d68662d8a98a91b72a62a9dc16f
```

Базовый тег:

```text
data-v1
```

Итоговый Git commit в `main`:

```text
cfb7d474f6570ebb8c8ccd340a7806140a43074d
```

Итоговый `data.dvc` указывает на каталог из двух файлов. Фактические SHA-256:

| Файл | SHA-256 | Строки | Столбцы |
|---|---|---:|---:|
| `data/iris.csv` | `3e1ba63f55da2aabc432d00b1670140f5162bf9ef34b837598ec2fc176c9ff26` | 150 | 7 |
| `data/wine.csv` | `38860ba04ace4d402242340bcf40be4bd6f4ebde9144a3dc89dc12c20f7f8e60` | 178 | 14 |

В Iris присутствуют исходные признаки, `target`, `sepal_area` и `petal_area`. В Wine присутствуют исходные признаки и `target`. Пропущенных значений нет.

DVC remote настроен в отдельной локальной директории вне Git-репозитория:

```text
../mlops-data-lozovoy-dvc-remote
```

CSV и DVC cache не добавляются в Git. В Git хранятся только `data.dvc`, код и конфигурация remote.

## 4. Ветки и merge

Созданы ветки:

- `feature/wine` — commit `41c12ae`, добавляет Wine;
- `feature/iris-features` — commits `53f53ea` и `55be311`, добавляет вычисляемые признаки Iris;
- merge обеих веток — commit `35e5d09`;
- объединение проверенной ветки в `main` — commit `cfb7d47`.

Во время merge был обнаружен конфликт в `data.dvc`. Обе версии были извлечены из DVC cache, сохранены отдельно, после чего итоговый workspace был собран из Iris с признаками и Wine. После этого `check_data.py` прошёл, а новый `data.dvc` был создан командой `dvc add data`.

## 5. Чистое восстановление

Репозиторий был клонирован в новую директорию без копирования старого workspace и cache. После `dvc pull` были восстановлены:

```text
data/iris.csv
data/wine.csv
```

Чистый clone прошёл `check_data.py`. SHA-256 и структура таблиц совпали с итоговой версией.

## 6. ClearML

Локально установлен ClearML SDK 2.1.12 и подготовлен скрипт `create_clearml_versions.py`. Скрипт создаёт следующие версии:

- project: `MIIT/MLOps/practice_3/lozovoy`;
- dataset name: `sklearn-tabular-lozovoy`;
- version `1.0.0`: исходный Iris, tag `base`;
- version `1.1.0`: дочерняя версия от `BASE_ID`, добавляет Wine;
- version `2.0.0`: отдельная дочерняя версия от `BASE_ID`, изменяет Iris признаками.

На момент выполнения работы ClearML server не был настроен: отсутствовали пользовательский `clearml.conf` и переменные подключения. Поэтому реальные `BASE_ID`, `WINE_ID` и `IRIS_FEATURES_ID` не создавались и намеренно не выдумывались. Для завершения ClearML-части нужно выполнить `clearml-init`, проверить server и запустить:

```bash
python create_clearml_versions.py --run
```

После запуска напечатанные IDs, parent IDs, состав файлов и SHA-256 нужно добавить в этот раздел отчёта.

## 7. Сравнение DVC и ClearML

| Критерий | DVC | ClearML Dataset |
|---|---|---|
| Идентификатор | Хэш в `.dvc`-метафайле | Уникальный Dataset ID |
| Метаданные | Git и `.dvc`-файлы | Dataset metadata и lineage на server |
| Содержимое | DVC cache и remote | Настроенное ClearML storage |
| Дочерняя версия | Новая Git-ветка и новый `.dvc` | `parent_datasets=[parent_id]` |
| Переключение | `git switch` + `dvc checkout` | `Dataset.get(dataset_id=...)` |
| Чистое восстановление | `git clone` + `dvc pull` | Получение Dataset по ID |
| Ветвление | Git branches | Parent lineage |
| Merge | Git merge с DVC merge driver | Новая Dataset version с выбранным parent |
| Связь с Git | Прямая: Git хранит `.dvc` | Может быть связана через отчёты и metadata |
| UI | Нет обязательного UI | Есть web-интерфейс и граф lineage |

## 8. Ответы на контрольные вопросы

1. Версию данных в DVC однозначно определяет хэш содержимого, записанный в `.dvc`-файле.
2. Git-коммита недостаточно без DVC remote: Git хранит метаданные и хэш, но не обязан содержать сами большие файлы.
3. Dataset version — человекочитаемый номер, а Dataset ID — уникальный идентификатор конкретного объекта версии.
4. `finalize()` делает текущую ClearML-версию immutable; он не создаёт следующую версию.
5. Нужно проверить, что parent ID версии `2.0.0` равен `BASE_ID`, а не `WINE_ID`.
6. После `git switch` без `dvc checkout` в workspace могут остаться файлы предыдущей версии.
7. DVC удобнее для проектов, где данные должны быть жёстко связаны с Git-ветками и коммитами. ClearML удобнее для web UI, lineage, обмена Dataset versions и связи данных с экспериментами.

## 9. Ограничения и безопасность

- В репозиторий не добавлены CSV, `.dvc/cache`, `.venv` и кэши.
- Credentials ClearML не записывались в код и отчёт.
- Локальный DVC remote находится вне репозитория.
- Файлы внутри DVC cache вручную не изменялись.
