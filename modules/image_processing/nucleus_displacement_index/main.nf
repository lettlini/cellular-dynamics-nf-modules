process nucleus_displacement_index {
    label "high_cpu", "long_running"

    input:
    tuple val(basename), path(labelled_nuclei_ds), path(labelled_cells_ds), path(graph_ds)
    val parent_dir_out

    output:
    tuple val(basename), path("graph_ds_with_nucleus_displacement_index.pickle"), emit: results

    script:
    """
    python ${projectDir}/cellular-dynamics-nf-modules/modules/image_processing/nucleus_displacement_index/scripts/main.py \
        --labelled_cell_infile=${labelled_cells_ds} \
        --labelled_nuclei_infile=${labelled_nuclei_ds} \
        --graph_ds_infile=${graph_ds} \
        --outfile="graph_ds_with_nucleus_displacement_index.pickle" \
        --cpus=${task.cpus}
    """
}
