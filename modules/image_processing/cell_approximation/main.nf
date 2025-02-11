process cell_approximation {

    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    conda "./environment.yml" 

    input:
    tuple val(basename), path(fpath)
    val cell_cutoff_px
    val parent_dir_out

    output:
    tuple val(basename), path("cell_approximation.pickle"), emit: results

    script:
    """
	 python ${moduleDir}/scripts/cell_approximation.py \
        --infile="${fpath}" \
        --outfile="cell_approximation.pickle" \
        --cell_cutoff_px=${cell_cutoff_px} \
        --cpus=${task.cpus}
    """
}
