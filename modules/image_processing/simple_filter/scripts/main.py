from argparse import ArgumentParser

import toml
from core_data_utils.datasets import BaseDataSet, BaseDataSetEntry
from core_data_utils.transformations import BaseFilter


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

    n, m = (
        dataset_config["data-preparation"]["remove_first_n"],
        dataset_config["data-preparation"]["remove_last_m"],
    )

    x = BaseDataSet.from_pickle(args.infile)

    x = FirstLastFilter(first_n=n, last_m=m)(x)

    x.to_pickle(args.outfile)
