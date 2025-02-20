process annotate_D2min {
    publishDir "${publish_dir}/${basename}", mode: 'copy'

    label "long_running", "low_cpu"

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(graph_dataset_fpath), path(dataset_config)
    val lag_times_minutes
    val minimum_neighbors
    val publish_dir

    output:
    tuple val(basename), path("D2min_annotated_graphs.pickle"), path(dataset_config), emit: results

    script:
    """
	 python ${moduleDir}/scripts/annotate_D2min.py \
        --infile=${graph_dataset_fpath} \
        --outfile="D2min_annotated_graphs.pickle" \
        --dataset_config=${dataset_config} \
        --lag_times_minutes=${lag_times_minutes} \
        --minimum_neighbors=${minimum_neighbors} \
        --cpus=${task.cpus}
    """
}
