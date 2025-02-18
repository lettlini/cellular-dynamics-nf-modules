process cell_approximation {

    publishDir "${publish_dir}/${basename}", mode: 'copy'

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(dataset_config), path(parent_config), path(fpath)
    val publish_dir

    output:
    tuple val(basename), path(dataset_config), path(parent_config), path("cell_approximation.pickle"), emit: results

    script:
    """
	 python ${moduleDir}/scripts/cell_approximation.py \
        --infile="${fpath}" \
        --outfile="cell_approximation.pickle" \
        --dataset_config=${dataset_config} \
        --parent_config=${parent_config} \
        --cpus=${task.cpus}
    """
}
