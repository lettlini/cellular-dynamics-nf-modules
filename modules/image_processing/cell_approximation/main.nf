process cell_approximation {

    publishDir "${publish_dir}/${basename}", mode: 'copy'

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(fpath), path(dataset_config)
    val cell_cutoff_mum
    val publish_dir

    output:
    tuple val(basename), path("cell_approximation.pickle"), path(dataset_config), emit: results

    script:
    """
	 python ${moduleDir}/scripts/cell_approximation.py \
        --infile="${fpath}" \
        --outfile="cell_approximation.pickle" \
        --dataset_config=${dataset_config} \
        --cell_cutoff_mum=${cell_cutoff_mum} \
        --cpus=${task.cpus}
    """
}
