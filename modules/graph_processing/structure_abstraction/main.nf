process structure_abstraction {
    publishDir "${params.parent_dir_out}/${basename}", mode: 'copy'

    input:
    tuple val(basename), path(nuclei_fpath), path(cell_fpath)

    output:
    tuple val(basename), path("abstract_structure.pickle"), emit: results

    script:
    """
    echo "Cell File Path: ${cell_fpath}, Basename: ${basename}"
    echo "Nuclei File Path: ${nuclei_fpath}, Basename: ${basename}"

    python ${projectDir}/cellular-dynamics-nf-modules/modules/graph_processing/structure_abstraction/scripts/structure_abstraction.py \
        --nuclei_infile="${nuclei_fpath}" \
        --cells_infile="${cell_fpath}" \
        --mum_per_px=${params.mum_per_px} \
        --outfile="abstract_structure.pickle" \
        --cpus=${task.cpus}
    """
}
