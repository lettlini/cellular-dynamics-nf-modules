from argparse import ArgumentParser

import numpy as np
import polars as pl


def concatenate_tracking_dataframes(file_paths: list[str]) -> pl.DataFrame:
    big_dataframe: pl.DataFrame = None
    current_last_track_id: int = 0

    for ds_path in file_paths:
        current_df = pl.read_ipc(
            ds_path,
            memory_map=False,
        )
        current_df = current_df.with_columns(
            (pl.col("track_id") + current_last_track_id).alias("track_id_unique")
        )
        current_last_track_id += current_df["track_id"].max()

        if big_dataframe is None:
            big_dataframe = current_df.clone()
        else:
            assert (
                np.intersect1d(
                    big_dataframe["track_id_unique"].to_numpy(),
                    current_df["track_id_unique"].to_numpy(),
                ).size
                == 0
            )
            big_dataframe = big_dataframe.vstack(
                current_df.select(big_dataframe.columns)
            )

    return big_dataframe


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--infile", required=True)
    parser.add_argument("--outfile", required=True)
    parser.add_argument("--cpus", required=True)
    args = parser.parse_args()

    with open(args.infile, "r", encoding="utf-8") as file:
        file_list = [line.strip() for line in file]

    df = concatenate_tracking_dataframes(file_list)

    df.write_ipc(args.outfile, compression="lz4")
