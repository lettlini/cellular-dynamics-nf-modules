process calculate_local_density {
    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    conda "${moduleDir}/environment.yml" 

    input:
    tuple val(basename), path(graph_dataset)
    val parent_dir_out

    output:
    tuple val(basename), path("graph_dataset_with_local_density.pickle"), emit: results

    script:
    """
	 python ${moduleDir}/scripts/calculate_local_density.py \
        --infile=${graph_dataset} \
        --outfile="graph_dataset_with_local_density.pickle" \
        --cpus=${task.cpus}
    """
}
