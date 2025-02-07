process annotate_neighbor_retention {
    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    input:
    tuple val(basename), path(graph_dataset_fpath)
    val delta_t_minutes
    val lag_times_minutes
    val parent_dir_out

    output:
    tuple val(basename), path("neighbor_retention_graph_ds.pickle"), emit: results

    script:
    """
	 python ${moduleDir}/scripts/annotate_neighbor_retention.py \
        --infile=${graph_dataset_fpath} \
        --outfile="neighbor_retention_graph_ds.pickle" \
        --delta_t_minutes=${delta_t_minutes} \
        --lag_times_minutes=${lag_times_minutes} \
        --cpus=${task.cpus}
    """
}
