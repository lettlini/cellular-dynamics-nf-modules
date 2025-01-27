process cage_relative_squared_displacement {

    label "short_running", "low_cpu"

    input:
    tuple val(basename), path(graph_dataset_fpath)
    val delta_t_minutes
    val lag_times_minutes
    val mum_per_px
    val parent_dir_out

    output:
    tuple val(basename), path("crsd_annotated_graphs.pickle"), emit: results

    script:
    """
    python ${projectDir}/cellular-dynamics-nf-modules/modules/tracking/cage_relative_squared_displacement/scripts/main.py \
            --infile=${graph_dataset_fpath} \
            --outfile="D2min_annotated_graphs.pickle" \
            --delta_t_minutes=${delta_t_minutes} \
            --lag_times_minutes=${lag_times_minutes} \
            --mum_per_px=${mum_per_px} \
            --cpus=${task.cpus}
    """
}
