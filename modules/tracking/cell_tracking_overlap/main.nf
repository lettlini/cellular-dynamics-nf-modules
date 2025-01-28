process cell_tracking_overlap {
    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    input:
    tuple val(basename), path(cell_approximation_fpath), path(abstract_structure_fpath)
    val parent_dir_out

    output:
    tuple val(basename), path("tracked_abstract_structure.pickle"), emit: results

    script:
    """
    python ${projectDir}/cellular-dynamics-nf-modules/modules/tracking/cell_tracking_overlap/scripts/track_cells.py \
        --cell_label_file=${cell_approximation_fpath} \
        --abstract_structure_file=${abstract_structure_fpath} \
        --outfile="tracked_abstract_structure.pickle" \
        --cpus=${task.cpus}
    """
}
