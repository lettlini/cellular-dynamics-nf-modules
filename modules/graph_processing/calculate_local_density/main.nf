process calculate_local_density {

    publishDir {
        path: "${parent_dir_out}/${basename}"
        enabled: workflow.debug
    }

    input:
    tuple val(basename), path(graph_dataset)
    val parent_dir_out

    output:
    tuple val(basename), path("graph_dataset_with_local_density.pickle"), emit: results

    script:
    """
    echo "Graph Dataset File Path: ${graph_dataset}, Basename: ${basename}"
    python ${projectDir}/cellular-dynamics-nf-modules/modules/graph_processing/calculate_local_density/scripts/calculate_local_density.py \
        --infile=${graph_dataset} \
        --outfile="graph_dataset_with_local_density.pickle" \
        --cpus=${task.cpus}
    """
}
