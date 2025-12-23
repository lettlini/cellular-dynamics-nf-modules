from argparse import ArgumentParser

from core_data_utils.datasets import BaseDataSet
from trackastra.model import Trackastra
import numpy as np


class TrackAstraTransform:
    """
    Track cells with 'TrackAstra', writing the label of the linked object in the
    next frame to the 'abstract_structure' dictionary.
    """

    def __init__(self, pretrained_id: str = "general_2d", device: str = "cpu"):
        self._model = Trackastra.from_pretrained(pretrained_id, device=device)

    def __call__(
        self,
        original_ds: BaseDataSet,
        labelled_cells_ds: BaseDataSet,
        abstract_structure_ds: BaseDataSet,
    ) -> dict:

        # make sure we don't alter this dataset outside of this scope
        abstract_structure_ds = abstract_structure_ds.copy()

        # turn original dataset into (t, X,Y,C) numpy array
        imgs = np.stack([entry.data.squeeze() for entry in original_ds], axis=0)
        # turn cell label image dataset into (t, X,Y) numpy array
        masks = np.stack([entry.data.squeeze() for entry in labelled_cells_ds], axis=0)

        # track with self._model (ignore cell division for now.)
        track_graph, _ = self._model.track(
            imgs=imgs, masks=masks, normalize_imgs=True, mode="greedy_nodiv"
        )

        # now we need to traverse the tracking graph while writing the labels to
        # the abstract strcuture dict.

        for graph_source, graph_target in track_graph.edges:
            # we need to find the current time:
            cdict = track_graph.nodes[graph_source]
            ctime = int(cdict["time"])

            actual_source = int(cdict["label"])
            actual_target = int(track_graph.nodes[graph_target]["label"])

            if "next_object_id" in abstract_structure_ds[ctime].data[actual_source]:
                raise RuntimeError(
                    f"Object (label={actual_source}, time={ctime}) was already linked."
                )

            abstract_structure_ds[ctime].data[actual_source][
                "next_object_id"
            ] = actual_target

        return abstract_structure_ds


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "--grayscale_file",
        required=True,
        type=str,
        help="Path to dataset containing grayscaled original images.",
    )

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

    grayscale_ds = BaseDataSet.from_pickle(args.grayscale_file)
    cell_label_ds = BaseDataSet.from_pickle(args.cell_label_file)
    astr_ds = BaseDataSet.from_pickle(args.abstract_structure_file)

    tracking_abstract_structure_ds = TrackAstraTransform()(
        original_ds=grayscale_ds,
        labelled_cells_ds=cell_label_ds,
        abstract_structure_ds=astr_ds,
    )

    tracking_abstract_structure_ds.to_pickle(args.outfile)
