import multiprocessing as mp
from argparse import ArgumentParser

import networkx as nx
import numpy as np
from core_data_utils.datasets import BaseDataSet, BaseDataSetEntry
from core_data_utils.transformations import BaseMultiDataSetTransformation
from nucleus_displacement_index import calculate_nusdi_single_frame


class CalculateNucleusDisplacementIndex(BaseMultiDataSetTransformation):

    def _transform_single_entry(
        self, entry: BaseDataSetEntry, dataset_properties: dict
    ) -> BaseDataSetEntry:
        cell_image: np.array = entry.data["cell_image"]
        nuclei_image: np.array = entry.data["nuclei_image"]
        graph: np.array = entry.data["graph"]

        nusdi_dict: dict[int, float] = calculate_nusdi_single_frame(
            cell_image, nuclei_image, dilate=False
        )

        nx.set_node_attributes(graph, nusdi_dict, "nucleus_displacement_index")

        return BaseDataSetEntry(identifier=entry.identifier, data=graph)

    def __call__(
        self,
        cpus: int,
        cell_image: BaseDataSet,
        nuclei_image: BaseDataSet,
        graph: BaseDataSet,
    ):
        return self._transform(
            cpus=cpus,
            copy_datasets=True,
            cell_image=cell_image,
            nuclei_image=nuclei_image,
            graph=graph,
        )


if __name__ == "__main__":
    mp.set_start_method("spawn")
    parser = ArgumentParser()
    parser.add_argument("--labelled_cell_infile", type=str, required=True)
    parser.add_argument("--labelled_nuclei_infile", type=str, required=True)
    parser.add_argument("--graph_ds_infile", type=str, required=True)
    parser.add_argument("--outfile", type=str, required=True)
    parser.add_argument("--cpus", type=int, required=True)

    args = parser.parse_args()

    # read in all required datasets
    labelled_cell_ds = BaseDataSet.from_pickle(args.labelled_cell_infile)
    labelled_nuclei_ds = BaseDataSet.from_pickle(args.labelled_nuclei_infile)
    graph_ds = BaseDataSet.from_pickle(args.graph_ds_infile)

    assert len(graph_ds) == len(labelled_cell_ds) == len(labelled_nuclei_ds)

    # calculate the nucleus displacement index and annotate nodes in graph
    x = CalculateNucleusDisplacementIndex()(
        cpus=args.cpus,
        cell_image=labelled_cell_ds,
        nuclei_image=labelled_nuclei_ds,
        graph=graph_ds,
    )

    # write to file
    x.to_pickle(args.outfile)
