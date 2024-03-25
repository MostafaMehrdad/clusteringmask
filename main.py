import pandas as pd
from typing import cast

THRESHOLD = 2.5
ROW = 52
COL = 55


def index_to_tuple(index: int) -> tuple[int, int]:
    return ((row := index // 52), index - row * 52)


def cleanse_file(file: str) -> pd.DataFrame:

    data: pd.DataFrame = pd.read_excel(file)
    data = data.rename(columns={"id": "index", "av(ppm)": "value"})
    data = cast(pd.DataFrame, data[~data["index"].isna()])
    data["tuple"] = data["index"].apply(index_to_tuple)
    data["row"] = data["tuple"].apply(lambda x: x[0]).astype(int)
    data["col"] = data["tuple"].apply(lambda x: x[1]).astype(int)
    return cast(pd.DataFrame, data[["row", "col", "value"]])


if __name__ == "__main__":
    df = cleanse_file("data/uBB-data.xlsx")
