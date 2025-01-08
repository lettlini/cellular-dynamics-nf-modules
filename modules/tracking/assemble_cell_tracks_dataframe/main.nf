process assemble_cell_track_dataframe {
    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    label "short_running", "low_cpu"

    input:
    tuple val(basename), path(graph_dataset_fpath)
    val delta_t_minutes
    val include_attrs
    val exclude_attrs
    val parent_dir_out

    output:
    tuple val(basename), path("cell_tracks.ipc"), emit: results

    script:
    """
    python ${projectDir}/cellular-dynamics-nf-modules/modules/tracking/assemble_cell_tracks_dataframe/scripts/assemble_tracking_df.py \
        --infile=${graph_dataset_fpath} \
        --outfile="cell_tracks.ipc" \
        --delta_t_minutes=${delta_t_minutes} \
        --include_attrs=${include_attrs} \
        --exclude_attrs=${exclude_attrs} \
        --cpus=${task.cpus}
    """
}
