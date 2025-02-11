from argparse import ArgumentParser
from typing import Iterable

import overlap_tracking
from core_data_utils.datasets import BaseDataSet, BaseDataSetEntry
from tqdm import trange


class OverlapTrackingTransformation:
    def __init__(self, labels_to_ignore: Iterable[int]) -> None:
        self._ignore_labels = labels_to_ignore

    def __call__(
        self, cell_labels: BaseDataSet, properties: BaseDataSet
    ) -> BaseDataSet:

        new_data_dict = {}
        properties = properties.copy()

        for i in trange(len(cell_labels)):
            centry = cell_labels[i]
            current_props = properties[i].data

            # if we are in the index range for tracking add tracking informtion
            # otherwise add properties unchanged as future processes will expect
            # nodes without tracking information rather than relying on index information
            if i < len(cell_labels) - 2:
                nentry = cell_labels[i + 1]

                current_tracking_map = (
                    overlap_tracking.single_timestep_overlap_tracking(
                        centry.data, nentry.data, self._ignore_labels
                    )
                )

                for current_label, next_label in current_tracking_map.items():
                    assert current_label in current_props
                    assert "next_object_id" not in current_props[current_label]
                    current_props[current_label]["next_object_id"] = next_label

            new_data_dict[centry.identifier] = BaseDataSetEntry(
                identifier=centry.identifier,
                data=current_props,
                metadata=centry.metadata,
            )

        return BaseDataSet(
            ds_metadata=cell_labels.metadata, dataset_entries=new_data_dict
        )


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "--cell_label_file",
        required=True,
        type=str,
        help="Path to dataset containing labelled cell masks.",
    )
    parser.add_argument(
        "--abstract_structure_file",
        required=True,
        type=str,
        help="Path to dataset containing cell structure abstraction.",
    )
    parser.add_argument(
        "--outfile", required=True, type=str, help="Path to output file."
    )
    parser.add_argument(
        "--cpus",
        required=True,
        type=int,
        help="CPU cores to use.",
    )

    args = parser.parse_args()

    cell_label_ds = BaseDataSet.from_pickle(args.cell_label_file)
    abstract_structure_ds = BaseDataSet.from_pickle(args.abstract_structure_file)

    tracking_abstract_structure_ds = OverlapTrackingTransformation((0,))(
        cell_labels=cell_label_ds, properties=abstract_structure_ds
    )

    tracking_abstract_structure_ds.to_pickle(args.outfile)
