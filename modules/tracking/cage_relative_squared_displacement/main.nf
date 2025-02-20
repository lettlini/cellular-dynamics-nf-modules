process cage_relative_squared_displacement {

    label "short_running", "low_cpu"

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(graph_dataset_fpath), path(dataset_config)
    val lag_times_minutes
    val parent_dir_out

    output:
    tuple val(basename), path("crsd_annotated_graphs.pickle"), path(dataset_config), emit: results

    script:
    """
	 python ${moduleDir}/scripts/main.py \
            --infile=${graph_dataset_fpath} \
            --outfile="crsd_annotated_graphs.pickle" \
            --lag_times_minutes=${lag_times_minutes} \
            --dataset_config=${dataset_config} \
            --cpus=${task.cpus}
    """
}
