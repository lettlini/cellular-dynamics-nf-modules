from argparse import ArgumentParser

import numpy as np
import toml
from core_data_utils.datasets import BaseDataSet, BaseDataSetEntry
from core_data_utils.transformations import BaseFilter
from scipy.signal import savgol_filter


def find_first_true(arr):
    if not arr.any():  # Check if any True exists
        return None  # or raise Exception, depending on your needs
    return int(np.argmax(arr))


def get_time_window(dataset: BaseDataSet, min_area_frac: float) -> tuple[int, int]:
    area_fractions = np.array([np.mean(entry.data > 0) for entry in dataset])
    area_fractions_smoothed = savgol_filter(area_fractions, 11, 3)
    area_fractions_valid = area_fractions_smoothed > min_area_frac

    front_drop = find_first_true(area_fractions_valid)

    back_drop = find_first_true(area_fractions_valid[::-1])
    if back_drop is not None:
        back_drop = len(dataset) - back_drop - 1

    return (
        front_drop,
        back_drop,
    )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--infile", required=True, type=str, help="Absolute path to input file"
    )
    parser.add_argument(
        "--outfile", required=True, type=str, help="Path to output file"
    )
    parser.add_argument(
        "--dataset_config",
        required=True,
        type=str,
        help="Drop first n entries from DataSet",
    )
    parser.add_argument(
        "--cpus",
        required=True,
        type=int,
        help="CPU cores to use.",
    )

    args = parser.parse_args()

    dataset_config = toml.load(args.dataset_config)

    min_area_fraction = dataset_config["data-preparation"]["min_area_fraction"]

    x = BaseDataSet.from_pickle(args.infile)

    n, m = get_time_window(x, min_area_fraction)

    if (n is not None) and (m is not None):
        assert m >= n, "invalid confluency time-window"

        if m - n > 0:
            x = x[n : m + 1].copy()
        else:
            x = BaseDataSet()
    else:
        x = BaseDataSet()

    x.to_pickle(args.outfile)
