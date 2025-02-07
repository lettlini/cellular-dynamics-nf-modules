process concatenate_tracking_dataframes {
    publishDir "${parent_dir_out}", mode: 'copy'

    label "single_threaded", "high_memory"

    input:
    val tracking_df_files_list
    val parent_dir_out

    output:
    path "all_cell_tracks.ipc"

    script:
    """
    echo '${tracking_df_files_list.join("\n")}' > file_list.txt
	 python ${moduleDir}/scripts/main.py \
        --infile='./file_list.txt' \
        --outfile='all_cell_tracks.ipc' \
        --cpus=${task.cpus}
    """
}
