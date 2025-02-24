process assemble_cell_track_dataframe {
    publishDir "${publish_dir}/${basename}", mode: 'symlink'

    label "short_running", "low_cpu"

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(graph_dataset_fpath), path(dataset_config)
    val include_attrs
    val exclude_attrs
    val publish_dir

    output:
    tuple val(basename), path("cell_tracks.ipc"), path(dataset_config), emit: results

    script:
    """
	 python ${moduleDir}/scripts/assemble_tracking_df.py \
        --infile=${graph_dataset_fpath} \
        --outfile="cell_tracks.ipc" \
        --dataset_config=${dataset_config} \
        --include_attrs=${include_attrs} \
        --exclude_attrs=${exclude_attrs} \
        --cpus=${task.cpus}
    """
}
