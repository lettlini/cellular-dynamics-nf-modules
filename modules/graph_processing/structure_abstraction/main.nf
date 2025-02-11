process structure_abstraction {
    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    conda "./environment.yml" 

    input:
    tuple val(basename), path(nuclei_fpath), path(cell_fpath)
    val mum_per_px
    val parent_dir_out

    output:
    tuple val(basename), path("abstract_structure.pickle"), emit: results

    script:
    """

	 python ${moduleDir}/scripts/structure_abstraction.py \
        --nuclei_infile="${nuclei_fpath}" \
        --cells_infile="${cell_fpath}" \
        --mum_per_px=${mum_per_px} \
        --outfile="abstract_structure.pickle" \
        --cpus=${task.cpus}
    """
}
