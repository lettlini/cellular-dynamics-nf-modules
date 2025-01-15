process annotate_graph_theoretical_observables {
    publishDir "${parent_dir_out}/${basename}", mode: 'copy'

    label "high_cpu", "long_running"

    input:
    tuple val(basename), path(graph_dataset_fpath)
    val parent_dir_out

    output:
    tuple val(basename), path("graph_dataset_annotated.pickle"), emit: results

    script:
    """
    echo "Graph Dataset File Path: ${graph_dataset_fpath}, Basename: ${basename}"
    python ${projectDir}/cellular-dynamics-nf-modules/modules/graph_processing/annotate_graph_theoretical_observables/scripts/graph_theory_annotations.py \
        --infile=${graph_dataset_fpath} \
        --outfile="graph_dataset_annotated.pickle" \
        --cpus=${task.cpus}
    """
}