process annotate_graph_theoretical_observables {
    publishDir "${parent_dir_out}/${basename}", mode: 'symlink'

    label "high_cpu", "long_running"

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(graph_dataset_fpath), path(dataset_config)
    val parent_dir_out

    output:
    tuple val(basename), path("graph_dataset_annotated.pickle"), path(dataset_config), emit: results

    script:
    """
	 python ${moduleDir}/scripts/graph_theory_annotations.py \
        --infile=${graph_dataset_fpath} \
        --outfile="graph_dataset_annotated.pickle" \
        --cpus=${task.cpus}
    """
}
