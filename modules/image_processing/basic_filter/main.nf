process basic_filter {

    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    label "low_cpu", "short_running"

    input:
    tuple val(basename), path(dataset_path)
    val drop_first_n
    val drop_last_m
    val parent_dir_out

    output:
    tuple val(basename), path("confluency_filtered.pickle"), emit: results

    script:
    """
	 python ${moduleDir}/scripts/filter.py \
        --infile="${dataset_path}" \
        --outfile="confluency_filtered.pickle" \
        --drop_first_n=${drop_first_n} \
        --drop_last_m=${drop_last_m} \
        --cpus=${task.cpus}
    """
}
