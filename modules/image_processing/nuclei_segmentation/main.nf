process nuclei_segmentation {
    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    label "high_cpu", "long_running"
    maxForks 1

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(dataset_config), path(parent_config), path(fpath)
    val publish_dir

    output:
    tuple val(basename), path(dataset_config), path(parent_config), path("nuclei_segmentation.pickle"), emit: results

    script:
    """
	 python ${moduleDir}/scripts/nuclei_segmentation.py \
        --infile="${fpath}" \
        --outfile="nuclei_segmentation.pickle" \
        --dataset_config=${dataset_config} \
        --parent_config=${parent_config} \
        --cpus=${task.cpus}
    """
}
