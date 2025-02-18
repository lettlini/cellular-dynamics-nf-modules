process basic_filter {

    publishDir "${publish_dir}/${basename}", mode: 'copy'

    label "low_cpu", "short_running"

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(dataset_config), path(parent_config), path(dataset_path)
    val publish_dir

    output:
    tuple val(basename), path(dataset_config), path(parent_config), path("confluency_filtered.pickle"), emit: results

    script:
    """
	 python ${moduleDir}/scripts/filter.py \
        --infile="${dataset_path}" \
        --outfile="confluency_filtered.pickle" \
        --dataset_config="${dataset_config}" \
        --parent_config="${parent_config}" \
        --cpus=${task.cpus}
    """
}
