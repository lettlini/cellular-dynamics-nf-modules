# Cellular Dynamics Nextflow Modules

A collection of Nextflow modules for analyzing cellular dynamics in cell monolayers using imaging data.

## Features

- Image processing modules for nuclei segmentation and cell approximation
- Cell tracking and trajectory analysis
- Graph-based analysis of cellular neighborhoods
- Measures for cellular motion ($D^2_\text{min}$, cage-relative squared displacement ($CRSD$))
- Structure and density analysis

## Quick Start

1. Add this repository as a submodule to your Nextflow pipeline:

```bash
git submodule add https://github.com/lettlini/cellular-dynamics-nf-modules
```

2. Import modules in your pipeline script:

```nextflow
include { nuclei_segmentation } from './cellular-dynamics-nf-modules/modules/image_processing/nuclei_segmentation/main.nf'
include { cage_relative_squared_displacement } from './cellular-dynamics-nf-modules/modules/tracking/cage_relative_squared_displacement/main.nf'
```

3. Use the modules in your workflow:

```nextflow
workflow {
    nuclei_segmentation(
        input_channel,
        stardist_probability_threshold,
        min_nucleus_area_pxsq,
        parent_dir_out
    )
}
```
