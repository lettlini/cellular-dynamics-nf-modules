from argparse import ArgumentParser
import networkx as nx
import numpy as np
from core_data_utils.datasets import BaseDataSet, BaseDataSetEntry
from core_data_utils.transformations import BaseDataSetTransformation


class CalculateLocalDensityTransformation(BaseDataSetTransformation):

    def _transform_single_entry(
        self, entry: BaseDataSetEntry, dataset_properties: dict
    ) -> BaseDataSetEntry:

        current_graph: nx.Graph = entry.data

        for nodeid, nodeprops in current_graph.nodes(data=True):
            areas = [nodeprops["cell_area_mum_squared"]]  # add own area to list

            # iterate over neighbors, adding their areas to the list
            for nb_index in current_graph.neighbors(nodeid):
                areas.append(current_graph.nodes[nb_index]["cell_area_mum_squared"])

            # local density is the inverse of the mean area of the node and its neighbors
            nodeprops["local_density_per_mum_squared"] = 1.0 / np.mean(areas)

        return BaseDataSetEntry(
            identifier=entry.identifier, data=current_graph, metadata=entry.metadata
        )


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "--infile",
        required=True,
        type=str,
        help="Path to input file.",
    )
    parser.add_argument(
        "--outfile",
        required=True,
        type=str,
        help="Path to output file.",
    )
    parser.add_argument(
        "--cpus",
        required=True,
        type=int,
        help="Path to output file.",
    )

    args = parser.parse_args()

    x = BaseDataSet.from_pickle(args.infile)

    x = CalculateLocalDensityTransformation()(x, cpus=1)

    x.to_pickle(args.outfile)
