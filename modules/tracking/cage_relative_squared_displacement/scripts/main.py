from argparse import ArgumentParser
from typing import Optional

import networkx as nx
import numpy as np
from core_data_utils.datasets import BaseDataSet
from tqdm import trange


def get_object_positions(graph_ds, node_label, sindex, prefix="cell"):
    node_x = graph_ds[sindex].data.nodes[node_label][f"{prefix}_centroid_x"]
    node_y = graph_ds[sindex].data.nodes[node_label][f"{prefix}_centroid_y"]

    position_vector = np.array([node_x, node_y])
    position_vector = position_vector[
        np.newaxis, :
    ]  # always return vector of shape (1,2)
    return position_vector


def get_future_node(
    graph_ds: BaseDataSet, node_label: int, lag_time_frames: int, sindex: int
) -> tuple[int, dict] | tuple[None, None]:

    if sindex + lag_time_frames + 1 >= len(graph_ds):
        return None, None
    if lag_time_frames == 0:
        return node_label

    current_label = node_label

    for i in range(lag_time_frames):
        nprops = graph_ds[sindex + i].data.nodes[current_label]
        if "next_object_id" not in nprops:
            return None, None
        current_label = nprops["next_object_id"]

    return current_label, graph_ds[sindex + lag_time_frames].data.nodes[current_label]


class CageRelativeSquaredDisplacementTransformation:
    def __init__(
        self,
        mum_per_px: float,
        lag_time_frames: int,
        property_suffix: str,
        property_string: Optional[str] = None,
    ) -> None:
        self._mum_per_px = mum_per_px
        self._lag_time_frames = lag_time_frames
        self._property_suffix = property_suffix
        self._property_string = (
            property_string
            if property_string is not None
            else "cage_relative_squared_displacement_mum_squared_"
        )
        self._full_property_string = f"{self._property_string}{self._property_suffix}"

    def crsd(
        self,
        current_position,
        future_position,
        neighbors_current_pos,
        neighbors_future_pos,
    ) -> float:

        if (neighbors_current_pos is None) and (neighbors_future_pos is None):
            return (np.linalg.norm(future_position - current_position) ** 2) * (
                self._mum_per_px**2
            )

        if (neighbors_current_pos is None) ^ (neighbors_future_pos is None):
            raise ValueError(
                "'neighbors_current_pos' and 'neighbors_future_pos' must be either both None or both not None"
            )

        node_displacement = future_position - current_position  # (1,2)
        neighbors_displacement = neighbors_future_pos - neighbors_current_pos  # (n,2)

        mean_neighbor_displacement = np.mean(neighbors_displacement, axis=0)  # (1,2)

        return (np.linalg.norm(node_displacement - mean_neighbor_displacement) ** 2) * (
            self._mum_per_px**2
        )

    def crsd_single_node(self, graph_ds, node_label, sindex) -> float:
        current_own_position = get_object_positions(
            graph_ds, node_label, sindex, prefix="cell"
        )

        future_own_label, future_own_props = get_future_node(
            graph_ds, node_label, self._lag_time_frames, sindex
        )

        if future_own_label is None:
            return np.NaN

        future_own_position = np.array(
            (future_own_props["cell_centroid_x"], future_own_props["cell_centroid_y"])
        )[np.newaxis, :]

        neighbors_current_positions = []
        neighbors_future_positions = []

        for nb in nx.neighbors(graph_ds[sindex].data, node_label):
            future_nb_label, future_nb_props = get_future_node(
                graph_ds, nb, self._lag_time_frames, sindex
            )

            if future_nb_label is not None:
                neighbors_current_positions.append(
                    get_object_positions(graph_ds, nb, sindex, prefix="cell")
                )
                neighbors_future_positions.append(
                    np.array(
                        (
                            future_nb_props["cell_centroid_x"],
                            future_nb_props["cell_centroid_y"],
                        )
                    )[np.newaxis, :]
                )

        assert len(neighbors_current_positions) == len(neighbors_future_positions)

        # if there are no neighbors or no neighbors were tracked long enough we
        # return the squared distance between the current and future position
        if len(neighbors_current_positions) == 0:
            return self.crsd(current_own_position, future_own_position, None, None)

        neighbors_current_positions = np.vstack(neighbors_current_positions)
        neighbors_future_positions = np.vstack(neighbors_future_positions)

        return self.crsd(
            current_own_position,
            future_own_position,
            neighbors_current_positions,
            neighbors_future_positions,
        )

    def __call__(self, graph_ds: BaseDataSet) -> BaseDataSet:

        graph_ds = graph_ds.copy()

        for sindex in trange(len(graph_ds)):
            for node_label in graph_ds[sindex].data.nodes:
                crsd = self.crsd_single_node(graph_ds, node_label, sindex)
                graph_ds[sindex].data.nodes[node_label][
                    self._full_property_string
                ] = crsd

        return graph_ds


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "--infile",
        required=True,
        type=str,
        help="Path to input file.",
    )
    parser.add_argument(
        "--lag_times_minutes",
        required=True,
        type=str,
        help="Comma separated list of lag times (in minutes)",
    )

    parser.add_argument(
        "--delta_t_minutes",
        required=True,
        type=int,
        help="Time difference between two adjacent frames.",
    )
    parser.add_argument(
        "--mum_per_px",
        required=True,
        type=float,
        help="Microns per pixel.",
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
        help="CPU cores to use.",
    )

    args = parser.parse_args()

    lag_times_minutes = [int(lt) for lt in args.lag_times_minutes.split(",")]
    lag_times_frames = [lt // args.delta_t_minutes for lt in lag_times_minutes]

    x = BaseDataSet.from_pickle(args.infile)

    for lt_frames, lt_minutes in zip(lag_times_frames, lag_times_minutes, strict=True):
        x = CageRelativeSquaredDisplacementTransformation(
            mum_per_px=args.mum_per_px,
            lag_time_frames=lt_frames,
            property_suffix=f"{lt_minutes}_min",
        )(x)

    x.to_pickle(args.outfile)
