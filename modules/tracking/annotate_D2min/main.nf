process annotate_D2min {
    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    label "long_running", "low_cpu"

    input:
    tuple val(basename), path(graph_dataset_fpath)
    val delta_t_minutes
    val lag_times_minutes
    val mum_per_px
    val minimum_neighbors
    val parent_dir_out

    output:
    tuple val(basename), path("D2min_annotated_graphs.pickle"), emit: results

    script:
    """
    python ${projectDir}/cellular-dynamics-nf-modules/modules/tracking/annotate_D2min/scripts/annotate_D2min.py \
        --infile=${graph_dataset_fpath} \
        --outfile="D2min_annotated_graphs.pickle" \
        --delta_t_minutes=${delta_t_minutes} \
        --lag_times_minutes=${lag_times_minutes} \
        --mum_per_px=${mum_per_px} \
        --minimum_neighbors=${minimum_neighbors} \
        --cpus=${task.cpus}
    """
}
