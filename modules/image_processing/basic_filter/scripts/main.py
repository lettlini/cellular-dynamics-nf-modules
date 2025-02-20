from argparse import ArgumentParser

from core_data_utils.datasets import BaseDataSet, BaseDataSetEntry
from core_data_utils.transformations import BaseFilter
import toml
import numpy as np
from scipy.signal import savgol_filter


def find_first_true(arr):
    if not arr.any():  # Check if any True exists
        return None  # or raise Exception, depending on your needs
    return np.argmax(arr)


def get_time_window(dataset: BaseDataSet, min_area_frac: float) -> tuple[int, int]:
    area_fractions = np.array([np.mean(entry.data > 0) for entry in dataset])
    area_fractions_smoothed = savgol_filter(area_fractions, 11, 3)
    area_fractions_valid = area_fractions_smoothed > min_area_frac

    return (
        find_first_true(area_fractions_valid),
        len(dataset) - find_first_true(area_fractions_valid[::-1]) - 1,
    )


class FirstLastFilter(BaseFilter):
    def __init__(self, first_n: int, last_m: int) -> None:

        # set filter parameters
        self.first_n = first_n
        self.last_m = last_m

        super().__init__()

    def _filter_decision_single_entry(
        self, index: int, _: BaseDataSetEntry, **kwargs
    ) -> bool:
        if (index < self.first_n) or (index >= kwargs["dataset_length"] - self.last_m):
            return False
        return True

    def _global_dataset_properties(self, dataset: BaseDataSet) -> dict:
        return {"dataset_length": len(dataset)}


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

    assert m >= n, "invalid confluency time-window"

    if (n is not None) and (m is not None):
        if m - n > 0:
            x = FirstLastFilter(first_n=n, last_m=m)(x)
        else:
            x = BaseDataSet()
    else:
        x = BaseDataSet()

    x.to_pickle(args.outfile)
