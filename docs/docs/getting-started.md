Implementing your own nextflow pipeline for you research on cellular dynamics in cell monolayers is easy.
This guide will shortly explain how to get started.

## Prerequesites

What you'll need:

1. [nextflow](https://www.nextflow.io/) installation

2. [miniforge](https://github.com/conda-forge/miniforge) [^1]

3. the `cmot-pipeline` python environment as defined in `environment.yml` [^2]

4. The `cellular-dynamics-nf-modules` repository downloaded in your project folder, e.g.

```
Your Project/
│
├── pipeline.nf
│
├── nextflow.config
│
└── cellular-dynamics-nf-modules/
    ├── modules/
    ├── docs/
    └── ...
```

## Simple Pipeline Example

### Defining the Pipeline Steps
In this section we develop a short pipeline that
1. loads our data
2. segments the nuclei (see [`nuclei_segmentation` module](./modules.md#nuclei-segmentation))
3. runs the cell approximation (see [`cell_approximation` module](./modules.md#cell-approximation))

In the pipeline definition (`pipeline.nf`) we start by importing the pre-defined nextflow processes
`nuclei_segmentation` and `cell_approximation`:

```nextflow
include { nuclei_segmentation } from './cellular-dynamics-nf-modules/modules/image_processing/nuclei_segmentation/main.nf'
include { cell_approximation } from './cellular-dynamics-nf-modules/modules/image_processing/cell_approximation/main.nf'
```

Next, we define a process that will read the raw image files and stores them in an instance of the
`python`-class [`BaseDataSet`](https://github.com/lettlini/core-data-utils/blob/f47e058826d6d9905e75b61b8f154815d876d788/core_data_utils/datasets/base_dataset.py#L48C1-L48C19).
This class is defined in the [`core-data-utils` repository](https://github.com/lettlini/core-data-utils) which provides the basic framework
for reading, storing and manipulating any kind of data we might need in our pipeline.

Create a new `python`-script called `prepare_data.py` with content similar to

```python
from argparse import ArgumentParser

import cv2
from core_data_utils.datasets import BaseDataSet, BaseDataSetEntry
from core_data_utils.datasets.image import ImageDataset


if __name__ == "__main__":

    cv2.setNumThreads(0)

    parser = ArgumentParser()
    parser.add_argument("--indir", type=str, required=True)
    parser.add_argument("--outfile", type=str, required=True)

    args = parser.parse_args()

    # this will read all images in the directory 'args.indir' and store them in 'x'
    x = ImageDataSet.from_directory(args.indir)

    # write dataset 'x' to disk via pickle
    x.to_pickle(args.outfile)
```

To call this script in our `nextflow` pipeline, define a _new process_
in `pipeline.nf`:

```nextflow
process prepare_dataset{

    label "low_cpu", "short_running" // can be used to control the amount of resources allocated for process by SLURM

    // define what inputs the process requires
    input:
    tuple val(basename), path(dataset_path)

    // define what the process will output
    output:
    tuple val(basename), path("original_dataset.pickle"), emit: results

    /*
    define what bash-script will be executed, in this case we simply call
    our python script 'prepare_dataset.py' and suppy it with the
    process's input arguments as 'command line arguments' (that's why we need
    an ArgumentParser in the python script).
    */
    script:
    """
    python ${projectDir}/scripts/prepare_dataset.py \
        --indir="${dataset_path}" \
        --outfile="original_dataset.pickle"
    """
}
```

With this preliminary process in place we can define the full pipeline:
```nextflow

workflow {
    // we create a queue-channel listing all dataset directories inside a common parent directory (params.parent_indir)
    // params.parent_indir can be supplied either via a config file or directly be specified
    input_datasets = Channel.fromPath(file(params.parent_indir).resolve(params.in_dir).toString(), type: "dir")

    // Transform the channel to emit both the directory and its basename
    // This creates a tuple channel: [dir, basename]
    input_datasets = input_datasets.map { dir ->
        def basename = dir.name
        [basename, dir]
    }

    // prepare datasets:
    prepare_dataset(input_datasets)

    /* the output of prepare_datasets is the input for the nuclei_segmentation
    in addition to the prepared dataset pickle file which is output by the previous process
    we also need to specify:
        1. the stardist probability threshold
        2. minimum nucleus area (in px^2)
        3. the directory to which the output should be published
    */
    nuclei_segmentation(prepare_dataset.out.results, 0.473, ...)

    /* the output of the nuclei segmentation is then fed to the 'cell_approximation'
    process: (for a more detailed documentation of the input parameters the processes expect see
    the corresponding module documentation)
    */
    cell_approximation(nuclei_segmentation.out.results, cell_cutoff_px, parent_dir_out)
}

```

### Run the Example Pipeline

To run the pipeline, run the following command from the directory the `pipeline.nf`
file resides in:

```bash
nextflow run ./pipeline.nf
```


[^1]: or another python distribution that comes with `conda` or `mamba`
[^2]: This environment contains **all** module dependencies. Depending on which ones you are planning
to use some dependencies might not be needed.

