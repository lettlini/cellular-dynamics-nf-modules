process build_graphs {
    publishDir "${publish_dir}/${basename}", mode: 'copy'

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(abstract_structure_fpath), path(dataset_config)
    val publish_dir

    output:
    tuple val(basename), path("graph_dataset.pickle"), path(dataset_config), emit: results

    script:
    """
	 python ${moduleDir}/scripts/build_graphs.py \
        --infile=${abstract_structure_fpath} \
        --dataset_config=${dataset_config} \
        --outfile="graph_dataset.pickle" \
        --cpus=${task.cpus}
    """
}
