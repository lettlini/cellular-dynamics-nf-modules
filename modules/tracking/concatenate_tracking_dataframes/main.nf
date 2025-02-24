process concatenate_tracking_dataframes {
    publishDir "${publish_dir}", mode: 'symlink'

    label "single_threaded", "high_memory"

    conda "${moduleDir}/environment.yml"

    input:
    val tracking_df_files_list
    val publish_dir

    output:
    path "all_cell_tracks.ipc", emit: results

    script:
    """
    echo '${tracking_df_files_list.join("\n")}' > file_list.txt
    python ${moduleDir}/scripts/main.py \
    --infile='./file_list.txt' \
    --outfile='all_cell_tracks.ipc' \
    --cpus=${task.cpus}
    """
}
