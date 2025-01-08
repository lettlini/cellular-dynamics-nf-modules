process cell_approximation {

    publishDir "${params.parent_dir_out}/${basename}", mode: 'copy'

    input:
    tuple val(basename), path(fpath)

    output:
    tuple val(basename), path("cell_approximation.pickle"), emit: results

    script:
    """
    echo "Dataset Path: ${fpath}, Basename: ${basename}"
    python ${projectDir}/cellular-dynamics-nf-modules/modules/image_processing/cell_approximation/scripts/cell_approximation.py \
        --infile="${fpath}" \
        --outfile="cell_approximation.pickle" \
        --cell_cutoff_px=${params.cell_cutoff_px} \
        --cpus=${task.cpus}
    """
}
