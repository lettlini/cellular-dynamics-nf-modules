process nuclei_segmentation_cellpose {
    publishDir "${publish_dir}/${basename}", mode: 'symlink'

    label "high_cpu", "long_running"

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(fpath), path(dataset_config)
    val min_nucleus_area_mumsq
    val publish_dir

    output:
    tuple val(basename), path("nuclei_segmentation_cellpose.pickle"), path(dataset_config), emit: results

    script:
    """
	 python ${moduleDir}/scripts/nuclei_segmentation_cellpose.py \
        --infile="${fpath}" \
        --outfile="nuclei_segmentation_cellpose.pickle" \
        --dataset_config=${dataset_config} \
        --min_nucleus_area_mumsq=${min_nucleus_area_mumsq} \
        --cpus=${task.cpus}
    """
}
