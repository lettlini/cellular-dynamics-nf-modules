import multiprocessing as mp
from argparse import ArgumentParser

import cv2
import numpy as np
from core_data_utils.datasets import BaseDataSet, BaseDataSetEntry
from core_data_utils.transformations import BaseDataSetTransformation


class CellApproximationTransformation(BaseDataSetTransformation):

    def __init__(self, cell_cutoff_px: int = None):
        self._cell_cutoff_px = cell_cutoff_px

        super().__init__()

    @staticmethod
    def get_disconnected(label_image: np.array, nuclei_mask: np.array):

        all_cell_labels = np.setdiff1d(label_image, (0,))
        disconnected_cell_labels = label_image.copy()

        _, nuclei_labelled = cv2.connectedComponents(
            nuclei_mask.astype(np.uint8), connectivity=8
        )

        height, width = label_image.shape

        for cell_label in all_cell_labels:

            corresponding_nucleus_label = np.setdiff1d(
                nuclei_labelled[label_image == cell_label], (0,)
            ).item()

            binary_cell_mask = label_image == cell_label

            num_labels, _ = cv2.connectedComponents(binary_cell_mask.astype(np.uint8))

            if num_labels > 2:
                # we have more than one connected component, keep only the largest one that has overlap with the
                # corresponding nucleus

                raise RuntimeError("More than one connected component in cell mask")

            contours, _ = cv2.findContours(
                binary_cell_mask.astype(np.uint8),
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_NONE,
            )

            assert len(contours) == 1

            contour = contours[0].squeeze()

            for column, row in contour:
                # only delete if the pixel is not part of the nuclei mask
                if nuclei_mask[row, column] == 0:
                    current_neighbors = disconnected_cell_labels[
                        max(0, row - 1) : min(height, row + 2),
                        max(0, column - 1) : min(width, column + 2),
                    ].flatten()

                    if np.setdiff1d(current_neighbors, (0, cell_label)).size > 0:
                        disconnected_cell_labels[row, column] = 0

            new_num_ccs, new_labelled, new_stats, _ = cv2.connectedComponentsWithStats(
                (disconnected_cell_labels == cell_label).astype(np.uint8),
                connectivity=8,
            )
            if new_num_ccs > 2:
                # removing pixels lead to two different connected components with the same label
                # we only keep the one that overlaps with the corresponding nucleus and is the largest
                overlapping_labels = np.setdiff1d(
                    new_labelled[nuclei_labelled == corresponding_nucleus_label], (0,)
                )

                # we wanto keep the largest CC that has overlap with the nucleus
                keep_index = overlapping_labels[
                    np.argmax(new_stats[overlapping_labels, cv2.CC_STAT_AREA], axis=0)
                ]

                # we set all other labels to zero
                disconnected_cell_labels[
                    np.logical_and(
                        disconnected_cell_labels == cell_label,
                        new_labelled != keep_index,
                    )
                ] = 0

        return disconnected_cell_labels

    def _transform_single_entry(
        self, entry: BaseDataSetEntry, dataset_properties: dict
    ) -> BaseDataSetEntry:
        image = entry.data

        num_nuclei, _ = cv2.connectedComponents(
            (image > 0).astype(np.uint8), connectivity=8
        )

        binary_nuclei_mask: np.array = (image > 0).astype(np.int8)

        # we pad the binary nuclei mask with zeros to avoid border effects
        binary_nuclei_mask = np.pad(
            binary_nuclei_mask, 1, mode="constant", constant_values=0
        )

        _, label_image = cv2.connectedComponents(binary_nuclei_mask)

        dislabels = label_image.copy().astype(np.int32)
        bg_mask = np.zeros_like(label_image, dtype=bool)
        inimage = cv2.distanceTransform(
            (label_image == 0).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE
        )

        if self._cell_cutoff_px is not None:
            bg_mask[inimage >= self._cell_cutoff_px] = True

        inimage = cv2.merge(3 * [inimage]).astype(np.uint8)

        dislabels = cv2.watershed(inimage, dislabels)

        # step 4: some post-processing
        dislabels[dislabels == -1] = 0  # set boundaries to 0

        dislabels = CellApproximationTransformation.get_disconnected(
            dislabels, binary_nuclei_mask
        )

        # limit cell area by distance transform
        if self._cell_cutoff_px is not None:
            dislabels[bg_mask] = 0

        # we remove the padding
        dislabels = dislabels[1:-1, 1:-1]

        # return a binary mask
        dislabels = (dislabels > 0).astype(np.uint8)

        num_cells, _ = cv2.connectedComponents(dislabels)

        assert (
            num_cells == num_nuclei
        ), f"Number of cells ({num_cells}) does not match number of nuclei ({num_nuclei})"

        return BaseDataSetEntry(
            identifier=entry.identifier, data=dislabels, metadata=entry.metadata
        )


if __name__ == "__main__":

    mp.set_start_method("spawn")

    cv2.setNumThreads(0)

    parser = ArgumentParser()
    parser.add_argument(
        "--infile", required=True, type=str, help="Absolute path to input file"
    )
    parser.add_argument(
        "--outfile", required=True, type=str, help="Path to output file"
    )
    parser.add_argument(
        "--cell_cutoff_px",
        required=True,
        type=float,
        help="Maximum radius of individual cells",
    )
    parser.add_argument(
        "--cpus",
        required=True,
        type=int,
        help="CPU cores to use.",
    )

    args = parser.parse_args()

    x = BaseDataSet.from_pickle(args.infile)

    x = CellApproximationTransformation(cell_cutoff_px=args.cell_cutoff_px)(
        dataset=x, cpus=args.cpus
    )

    x.to_pickle(args.outfile)
