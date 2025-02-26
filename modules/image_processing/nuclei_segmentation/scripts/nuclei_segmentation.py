import os
from argparse import ArgumentParser

import cv2
import numpy as np
import toml
from core_data_utils.datasets import BaseDataSet, BaseDataSetEntry
from core_data_utils.transformations import BaseDataSetTransformation
from stardist.models import StarDist2D


def get_disconnected(labels):
    """
    Disconnect touching regions with different labels (stardist).

    Args:
        labels (np.array): Label image.

    Returns:
        (np.array): Disconnected label image.
    """

    disconnected_labels = labels.copy()
    all_labels = np.setdiff1d(disconnected_labels, (0,))  # ignore background

    height, width = disconnected_labels.shape

    for cl in all_labels:
        mask = disconnected_labels == cl  # binary object mask

        # check whether there are more than one connected components
        num_ccs, labelled_ccs, stats, _ = cv2.connectedComponentsWithStats(
            mask.astype(np.uint8), connectivity=8
        )

        if num_ccs > 2:
            # delete all but the largest connected component
            keep_label = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
            mask[labelled_ccs != keep_label] = 0

        contours, _ = cv2.findContours(
            mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )

        assert len(contours) == 1, f"More than one contour found for label {cl}."

        contour_points = contours[0].squeeze()

        for column, row in contour_points:
            current_neighbors = disconnected_labels[
                max(0, row - 1) : min(height, row + 2),
                max(0, column - 1) : min(width, column + 2),
            ].flatten()

            # only delete pixel if necessary
            if np.setdiff1d(current_neighbors, (0, cl)).size > 0:
                disconnected_labels[row, column] = 0

    return disconnected_labels


class MinMaxScaleTransform(BaseDataSetTransformation):
    def _transform_single_entry(
        self, entry: BaseDataSetEntry, dataset_properties: dict
    ) -> BaseDataSetEntry:

        new_image = entry.data

        minval, maxval = np.min(new_image), np.max(new_image)
        new_image = (new_image - minval) / (maxval - minval)

        return BaseDataSetEntry(identifier=entry.identifier, data=new_image)


class GrayScaleTransform(BaseDataSetTransformation):
    def _transform_single_entry(
        self, entry: BaseDataSetEntry, dataset_properties: dict
    ) -> BaseDataSetEntry:

        image = entry.data

        new_image = image.mean(axis=2)
        return BaseDataSetEntry(identifier=entry.identifier, data=new_image)


class StarDistSegmentationTransform(BaseDataSetTransformation):
    def __init__(
        self,
        prob_threshold: float | None = None,
        num_tiles: int = 1,
    ):
        self._probability_threshold: float = prob_threshold
        self._stardist_model = StarDist2D.from_pretrained("2D_versatile_fluo")
        self._num_tiles = num_tiles

        super().__init__()

    def _transform_single_entry(
        self, entry: BaseDataSetEntry, dataset_properties: dict
    ) -> BaseDataSetEntry:

        image = entry.data

        labels, info = self._stardist_model.predict_instances(
            image, show_tile_progress=False, n_tiles=(self._num_tiles, self._num_tiles)
        )

        # We need to disconnect touching labels:
        labels = get_disconnected(labels)

        if self._probability_threshold is not None:
            for j in range(len(info["prob"])):
                if info["prob"][j] < self._probability_threshold:
                    labels[labels == j + 1] = 0

        # convert label image to binary mask
        labels = (labels > 0).astype(np.int8)

        return BaseDataSetEntry(
            identifier=entry.identifier, data=labels, metadata=entry.metadata
        )


class RemoveSmallObjectsTransform(BaseDataSetTransformation):
    def __init__(
        self,
        min_nuc_area_px2: float,
    ) -> None:
        self._min_nuclei_area_px = min_nuc_area_px2

        super().__init__()

    def _transform_single_entry(
        self, entry: BaseDataSetEntry, dataset_properties: dict
    ) -> BaseDataSetEntry:

        image = entry.data

        image = (image > 0).astype(np.int8)

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(image)

        for component_idx in range(1, num_labels):
            if stats[component_idx, 4] < self._min_nuclei_area_px:
                labels[labels == component_idx] = 0

        # convert label image to binary mask
        labels = (labels > 0).astype(np.int8)

        return BaseDataSetEntry(identifier=entry.identifier, data=labels)


if __name__ == "__main__":

    cv2.setNumThreads(0)

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
    )
    parser.add_argument(
        "--min_nucleus_area_mumsq",
        required=True,
        type=float,
    )
    parser.add_argument(
        "--cpus",
        required=True,
        type=int,
        help="CPU cores to use.",
    )

    args = parser.parse_args()

    full_config = toml.load(args.dataset_config)

    stardist_tiles = full_config["data-preparation"]["stardist_tiles"]

    stardist_thresh = None
    if "stardist_probality_threshold":
        stardist_thresh = full_config["data-preparation"][
            "stardist_probality_threshold"
        ]

    x = BaseDataSet.from_pickle(args.infile)

    x = GrayScaleTransform()(x)
    x = MinMaxScaleTransform()(x)

    min_nucleus_area_pxsq = args.min_nucleus_area_mumsq / (
        full_config["experimental-parameters"]["mum_per_px"] ** 2
    )

    x = StarDistSegmentationTransform(
        prob_threshold=stardist_thresh,
        num_tiles=stardist_tiles,
    )(dataset=x)
    x = RemoveSmallObjectsTransform(min_nuc_area_px2=min_nucleus_area_pxsq)(dataset=x)

    x.to_pickle(args.outfile)
