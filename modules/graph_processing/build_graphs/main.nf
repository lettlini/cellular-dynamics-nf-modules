process build_graphs {
    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    conda "${moduleDir}/environment.yml" 

    input:
    tuple val(basename), path(abstract_structure_fpath)
    val mum_per_px
    val parent_dir_out

    output:
    tuple val(basename), path("graph_dataset.pickle"), emit: results

    script:
    """
	 python ${moduleDir}/scripts/build_graphs.py \
        --infile=${abstract_structure_fpath} \
        --mum_per_px=${mum_per_px} \
        --outfile="graph_dataset.pickle" \
        --cpus=${task.cpus}
    """
}
