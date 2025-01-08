process basic_filter {

    publishDir "${params.parent_dir_out}/${basename}", mode: 'copy'

    label "low_cpu", "short_running"

    input:
    tuple val(basename), path(dataset_path)

    output:
    tuple val(basename), path("confluency_filtered.pickle"), emit: results

    script:
    """
    echo "Dataset Path: ${dataset_path}, Basename: ${basename}"
    python ${projectDir}/cellular-dynamics-nf-modules/image_processing/basic_filter/scripts/filter.py \
        --infile="${dataset_path}" \
        --outfile="confluency_filtered.pickle" \
        --drop_first_n=${params.drop_first_n} \
        --drop_last_m=${params.drop_last_m} \
        --cpus=${task.cpus}
    """
}
