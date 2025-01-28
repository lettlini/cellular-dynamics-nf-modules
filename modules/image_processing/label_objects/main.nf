process label_objects {
    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    label "short_running"

    input:
    tuple val(basename), path(fpath)
    val objects_name
    val parent_dir_out

    output:
    tuple val(basename), path("${objects_name}_labelled.pickle"), emit: results

    script:
    """
    python ${projectDir}/cellular-dynamics-nf-modules/modules/image_processing/label_objects/scripts/label_objects.py \
        --infile=${fpath} \
        --outfile="${objects_name}_labelled.pickle" \
        --cpus=${task.cpus}
    """
}
