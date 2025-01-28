process calculate_local_density {
    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    input:
    tuple val(basename), path(graph_dataset)
    val parent_dir_out

    output:
    tuple val(basename), path("graph_dataset_with_local_density.pickle"), emit: results

    script:
    """
    python ${projectDir}/cellular-dynamics-nf-modules/modules/graph_processing/calculate_local_density/scripts/calculate_local_density.py \
        --infile=${graph_dataset} \
        --outfile="graph_dataset_with_local_density.pickle" \
        --cpus=${task.cpus}
    """
}
