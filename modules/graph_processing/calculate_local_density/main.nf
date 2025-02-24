process calculate_local_density {
    publishDir "${publish_dir}/${basename}", mode: 'symlink'

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(graph_dataset), path(dataset_config)
    val publish_dir

    output:
    tuple val(basename), path("graph_dataset_with_local_density.pickle"), path(dataset_config), emit: results

    script:
    """
	 python ${moduleDir}/scripts/calculate_local_density.py \
        --infile=${graph_dataset} \
        --outfile="graph_dataset_with_local_density.pickle" \
        --cpus=${task.cpus}
    """
}
