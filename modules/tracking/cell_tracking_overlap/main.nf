process cell_tracking_overlap {
    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    conda "${moduleDir}/environment.yml" 

    input:
    tuple val(basename), path(cell_approximation_fpath), path(abstract_structure_fpath)
    val parent_dir_out

    output:
    tuple val(basename), path("tracked_abstract_structure.pickle"), emit: results

    script:
    """
	 python ${moduleDir}/scripts/track_cells.py \
        --cell_label_file=${cell_approximation_fpath} \
        --abstract_structure_file=${abstract_structure_fpath} \
        --outfile="tracked_abstract_structure.pickle" \
        --cpus=${task.cpus}
    """
}
