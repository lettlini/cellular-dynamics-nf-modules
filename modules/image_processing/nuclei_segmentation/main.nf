process nuclei_segmentation {
    publishDir "${params.parent_dir_out}/${basename}", mode: 'copy'

    label "high_cpu", "long_running"
    maxForks 1

    input:
    tuple val(basename), path(fpath)

    output:
    tuple val(basename), path("nuclei_segmentation.pickle"), emit: results

    script:
    """
    echo "Dataset Path: ${fpath}, Basename: ${basename}"
    python ${projectDir}/cellular-dynamics-nf-modules/image_processing/scripts/nuclei_segmentation.py \
        --infile="${fpath}" \
        --outfile="nuclei_segmentation.pickle" \
        --stardist_probility_threshold=${params.stardist_probality_threshold} \
        --min_nucleus_area_pxsq=${params.min_nucleus_area_pxsq} \
        --cpus=${task.cpus}
    """
}
