process confluency_filter {

    publishDir "${publish_dir}/${basename}", mode: 'copy'

    label "low_cpu", "short_running"

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(dataset_path), path(dataset_config)
    val object_filter
    val publish_dir

    output:
    tuple val(basename), path("${object_filter}_confluency_filtered.pickle"), path(dataset_config), emit: results

    script:
    """
	 python ${moduleDir}/scripts/main.py \
        --infile="${dataset_path}" \
        --outfile="${object_filter}_confluency_filtered.pickle" \
        --dataset_config="${dataset_config}" \
        --cpus=${task.cpus}
    """
}
