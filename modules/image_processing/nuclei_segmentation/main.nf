process nuclei_segmentation {
    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    label "high_cpu", "long_running"
    maxForks 1

    input:
    tuple val(basename), path(fpath)
    val stardist_probability_threshold
    val min_nucleus_area_pxsq
    val parent_dir_out

    output:
    tuple val(basename), path("nuclei_segmentation.pickle"), emit: results

    script:
    """
    python ${projectDir}/cellular-dynamics-nf-modules/modules/image_processing/nuclei_segmentation/scripts/nuclei_segmentation.py \
        --infile="${fpath}" \
        --outfile="nuclei_segmentation.pickle" \
        --stardist_probility_threshold=${stardist_probability_threshold} \
        --min_nucleus_area_pxsq=${min_nucleus_area_pxsq} \
        --cpus=${task.cpus}
    """
}
