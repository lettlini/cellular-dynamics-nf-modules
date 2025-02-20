process label_objects {
    publishDir "${publish_dir}/${basename}", mode: 'copy'

    label "short_running"

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(fpath), path(dataset_config)
    val objects_name
    val publish_dir

    output:
    tuple val(basename), path("${objects_name}_labelled.pickle"), path(dataset_config), emit: results

    script:
    """
	 python ${moduleDir}/scripts/label_objects.py \
        --infile=${fpath} \
        --outfile="${objects_name}_labelled.pickle" \
        --cpus=${task.cpus}
    """
}
