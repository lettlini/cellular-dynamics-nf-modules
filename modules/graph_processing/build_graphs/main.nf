process build_graphs {
    publishDir "${params.parent_dir_out}/${basename}", mode: 'copy'

    input:
    tuple val(basename), path(abstract_structure_fpath)

    output:
    tuple val(basename), path("graph_dataset.pickle"), emit: results

    script:
    """
    echo "Abstract Structure Path: ${abstract_structure_fpath}, Basename: ${basename}"
    python ${projectDir}/cellular-dynamics-nf-modules/modules/graph_processing/build_graphs/scripts/build_graphs.py \
        --infile=${abstract_structure_fpath} \
        --mum_per_px=${params.mum_per_px} \
        --outfile="graph_dataset.pickle" \
        --cpus=${task.cpus}
    """
}
