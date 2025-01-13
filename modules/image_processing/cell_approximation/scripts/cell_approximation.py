from argparse import ArgumentParser

import cv2
import numpy as np
from core_data_utils.datasets import BaseDataSet, BaseDataSetEntry
from core_data_utils.transformations import BaseDataSetTransformation
import multiprocessing as mp


def get_disconnected(timage: np.array) -> np.array:
    """Disconnects touching regions with different labels (stardist)"""

    dmask = np.zeros_like(timage)

    # get list of labels
    lls = np.unique(timage)
    lls = np.setdiff1d(lls, (0,))

    for current_label in lls:
        current_small_image = (timage == current_label).astype(np.uint8)
        current_small_image = cv2.erode(
            current_small_image, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        )
        dmask += current_small_image

    return ~(dmask.astype(bool))


class CellApproximationTransform(BaseDataSetTransformation):
    def __init__(self, cell_cutoff_px: int):
        self._cell_cutoff_px = cell_cutoff_px

        super().__init__()

    def _transform_single_entry(
        self, entry: BaseDataSetEntry, dataset_properties: dict
    ) -> BaseDataSetEntry:
        """Function to convert nuclei brightfield microscopy images (grayscale) to cell masks"""

        image = entry.data

        binary_nuclei_mask: np.array = (image > 0).astype(np.int8)
        _, label_image = cv2.connectedComponents(binary_nuclei_mask)

        dislabels = label_image.copy().astype(np.int32)
        bg_mask = np.ones_like(label_image)
        inimage = cv2.distanceTransform(
            (label_image == 0).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE
        )

        if self._cell_cutoff_px is not None:
            bg_mask[inimage >= self._cell_cutoff_px] = 0

        inimage = cv2.merge(3 * [inimage]).astype(np.uint8)

        dislabels = cv2.watershed(inimage, dislabels)

        # step 4: some post-processing
        dislabels[dislabels == -1] = 0  # set boundaries to 0
        dislabels[get_disconnected(dislabels) == 1] = 0

        if self._cell_cutoff_px is not None:
            dislabels[bg_mask == 0] = 0

        dislabels = self._ensure_cell_integrity(
            nuclei_labelled=label_image, cell_approximation=dislabels
        )

        dislabels = (dislabels > 0).astype(np.int8)

        return BaseDataSetEntry(identifier=entry.identifier, data=dislabels)

    def _ensure_cell_integrity(
        self, nuclei_labelled: np.array, cell_approximation: np.array
    ) -> np.array:
        """
        Ensure that each nucleus has exactly one associated connected component
        in the cell-approximation mask by removing all connected components in
        the cell approximation that have no overlap with the nucleus and
        subsequently only keeping the largest cell connected component.

        Args:
            nuclei_labelled (np.array): 2D np.array of labelled nuclei
            cell_approximation (np.array): 2D np.array of labelled cells
        Returns:
            (np.array): cell approximation mask with only the largest overlapping
                connected components present
        """

        all_nuclei_labels = np.setdiff1d(nuclei_labelled, (0,))
        set_zero_mask = np.zeros_like(cell_approximation, dtype=bool)

        for nl in all_nuclei_labels:
            # we need to check whether there are more than 1 connected components
            current_mask = (cell_approximation == nl).astype(np.int8)
            num_labels, lbim, stats, _ = cv2.connectedComponentsWithStats(
                current_mask, connectivity=8
            )

            assert num_labels > 0, f"Nucleus {nl} has no overlapping cells."

            if num_labels > 2:  # first label: bg, second label: 1st cc,...
                # we have more than 1 connected component for a single nucleus
                all_related_ccs = np.setdiff1d(lbim[cell_approximation == nl], (0,))
                overlapping_labels = np.unique(
                    lbim[np.logical_and(nuclei_labelled == nl, lbim != 0)]
                )

                # we wanto keep the largest CC that has overlap with the nucleus
                keep_index = overlapping_labels[
                    np.argmax(stats[overlapping_labels, 4], axis=0)
                ]

                # flag connected components for removal:
                for cc_index in all_related_ccs:
                    if cc_index != keep_index:
                        set_zero_mask[lbim == cc_index] = 1

            # else: we do nothing, everything is in order for this nucleus

        ret_image = cell_approximation.copy()
        ret_image[set_zero_mask] = 0

        return ret_image


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

    x = CellApproximationTransform(cell_cutoff_px=args.cell_cutoff_px)(
        dataset=x, cpus=args.cpus
    )

    x.to_pickle(args.outfile)
