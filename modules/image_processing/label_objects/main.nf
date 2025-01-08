process label_objects {
    publishDir "${params.parent_dir_out}/${basename}", mode: 'copy'

    label "short_running"

    input:
    tuple val(basename), path(fpath)

    output:
    tuple val(basename), path("cells_labelled.pickle"), emit: results

    script:
    """
    echo "Cell File Path: ${fpath}, Basename: ${basename}"
    python ${projectDir}/cellular-dynamics-nf-modules/image_processing/label_objects/scripts/label_objects.py \
        --infile=${fpath} \
        --outfile="cells_labelled.pickle" \
        --cpus=${task.cpus}
    """
}
