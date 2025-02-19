process structure_abstraction {
    publishDir "${publish_dir}/${basename}", mode: 'copy'

    conda "${moduleDir}/environment.yml"

    input:
    tuple val(basename), path(nuclei_fpath), path(cell_fpath), path(dataset_config)
    val publish_dir

    output:
    tuple val(basename), path("abstract_structure.pickle"), path(dataset_config), emit: results

    script:
    """
	 python ${moduleDir}/scripts/structure_abstraction.py \
        --infile_cells="${cell_fpath}" \
        --infile_nuclei="${nuclei_fpath}" \
        --outfile="abstract_structure.pickle" \
        --dataset_config="${dataset_config}" \
        --cpus=${task.cpus}
    """
}
