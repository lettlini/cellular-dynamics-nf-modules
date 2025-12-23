process cell_tracking_trackastra {
    publishDir "${publish_dir}/${basename}", mode: 'symlink'

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(grayscaled_fpath), path(cells_labelled_fpath), path(abstract_structure_fpath), path(dataset_config)
    val publish_dir

    output:
    tuple val(basename), path("tracked_abstract_structure_astra.pickle"), path(dataset_config), emit: results

    script:
    """
	 python ${moduleDir}/scripts/main.py \
        --grayscale_file=${grayscaled_fpath} \
        --cell_label_file=${cells_labelled_fpath} \
        --abstract_structure_file=${abstract_structure_fpath} \
        --outfile="tracked_abstract_structure_astra.pickle" \
        --cpus=${task.cpus}
    """
}
