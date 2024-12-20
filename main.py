import pandas as pd
from typing import cast
from dotenv import load_dotenv  # type: ignore
import os
import sys

sys.setrecursionlimit(10**6)

def read_file(file: str) -> pd.DataFrame:
    data: pd.DataFrame = pd.read_excel(file)
    data = cast(pd.DataFrame, data[~data["id"].isna()])
    data["id"] = data["id"].astype(int)
    data = data.rename(columns={"id": "index", "av(ppm)": "value"})
    return data


def index_to_tuple(index: int, column_quantity: int) -> tuple[int, int]:
    return (int(row := (index - 1) // column_quantity + 1), int(index - (row - 1) * column_quantity))


def get_points(df: pd.DataFrame, column_quantity: int) -> dict[tuple[int, int], float]:

    df["tuple"] = df["index"].apply(index_to_tuple, column_quantity=column_quantity)
    return {
        x["tuple"]: x["value"]
        for _, x in cast(pd.DataFrame, df[["tuple", "value"]]).to_dict("index").items()
    }


def find_neighbours(index: tuple[int, int]) -> list[tuple[int, int]]:
    return [
        (index[0] + i, index[1] + j)
        for i in range(-1, 2)
        for j in range(-1, 2)
        if i != 0 or j != 0
    ]


def get_cluster(
    index: tuple[int, int], points: set[tuple[int, int]]
) -> list[tuple[int, int]]:
    """
    get_cluster takes one point and all the eligible points
    returns the list of all points in the cluster with the input point
    """
    cluster: list[tuple[int, int]] = [index]
    stack = [x for x in find_neighbours(index) if x in points]
    cluster.extend(stack)
    points -= set(stack)
    
    while stack:
        current_point = stack.pop()
        eligible_neighbours = [x for x in find_neighbours(current_point) if x in points]
        points -= set(eligible_neighbours)
        cluster.extend(eligible_neighbours)
        stack.extend(eligible_neighbours)

    return cluster


def find_clusters(
    points: dict[tuple[int, int], float], threshold: float
) -> dict[int, list[tuple[int, int]]]:

    result: dict[int, list[tuple[int, int]]] = {}
    result[0] = [p for p, v in points.items() if v < threshold]

    eligible_points = {p: v for p, v in points.items() if v >= threshold}
    remaining_points = set(eligible_points.keys())

    cluster_counter = 1
    while remaining_points:
        current_point = remaining_points.pop()
        cluster_points = get_cluster(current_point, remaining_points)
        result[cluster_counter] = cluster_points
        cluster_counter += 1
    return result


def create_cluster_df(
    clusters_dict: dict[int, list[tuple[int, int]]], column_quantity: int
) -> pd.DataFrame:
    index_to_cluster = {
        (z[0] - 1) * column_quantity + z[1]: x for x, y in clusters_dict.items() for z in y
    }
    return pd.DataFrame.from_dict(index_to_cluster, orient="index").rename(
        columns={0: "cluster"}
    )

def main(file_name: str) -> None:
    load_dotenv(override=True)
    threshold = float(os.environ.get("THRESHOLD", 0))
    print(threshold)
    col = int(os.environ.get("COL", 0))
    if not threshold or not col:
        raise ValueError("please populate .env file with proper values.")

    df = read_file(file_name)
    points = get_points(df.copy(deep=True), col)
    clusters = find_clusters(points, threshold)
    cluster_df = create_cluster_df(clusters, col)
    df.set_index("index", inplace=True)
    result_df = df.join(cluster_df)
    result_df.reset_index(inplace=True)

    if not os.path.isdir("output"):
        os.mkdir("output")
    result_df.rename(columns={"index": "id", "value": "av(ppm)"}, inplace=True)
    
    base_name = os.path.splitext(os.path.split(file_name)[-1])[0]
    name_with_suffix = f"{base_name}-BKNM.xlsx"
    target = os.path.join("output", name_with_suffix)
    
    print("Writing into", target)
    result_df.to_excel(target, index=False)

if __name__ == "__main__":
    main(sys.argv[1])
