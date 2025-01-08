process annotate_D2min {
    publishDir "${params.parent_dir_out}/${basename}", mode: 'copy'

    label "long_running", "low_cpu"

    input:
    tuple val(basename), path(graph_dataset_fpath)

    output:
    tuple val(basename), path("D2min_annotated_graphs.pickle"), emit: results

    script:
    """
    echo "Graph Dataset File Path: ${graph_dataset_fpath}, Basename: ${basename}"
    python ${projectDir}/cellular-dynamics-nf-modules/modules/tracking/annotate_D2min/scripts/annotate_D2min.py \
        --infile=${graph_dataset_fpath} \
        --outfile="D2min_annotated_graphs.pickle" \
        --delta_t_minutes=${params.delta_t_minutes} \
        --lag_times_minutes=${params.lag_times_minutes} \
        --mum_per_px=${params.mum_per_px} \
        --minimum_neighbors=${params.minimum_neighbors} \
        --cpus=${task.cpus}
    """
}
