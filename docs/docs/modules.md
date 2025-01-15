# Module Documentation

This repository currently contains the following groups of modules:

1. image processing modules (`modules/image_processing`)
2. tracking modules (`modules/tracking/`)
3. graph processing modules (`modules/graph_processing`)

## Image Processing Modules

### Nuclei Segmentation
The `nuclei_segmentation` module provides a process that takes a
`BaseDataSet` instance with confocal microscopy images (RGB)  showing stained nuclei
as input. Subsequently, the images are grayscaled and re-scaled to the range `[0,1]`
before nuclei are segmented via [stardist](https://github.com/stardist/stardist).

Import the module into your pipeline script via

```nextflow
include { nuclei_segmentation } from './cellular-dynamics-nf-modules/modules/image_processing/nuclei_segmentation/main.nf'
```

|Argument Index | Argument Name|Argument Type|Description|
|-|-|-|-|
|1||tuple(val, path)|(`basename`, `fpath`)|
|2|`stardist_probability_threshold`|val|Floating point number defining `stardist` probability threshold.|
|3|`min_nucleus_area_pxsq`|val|Floating point number defining the minimum nucleus area (in $px^2$!). Segmented objects smaller than this will be removed.|
|4|`parent_dir_out`|val|Directory to which the resulting file will be published.|


### Basic Filter
### Cell Approximation
### Label Objects

## Tracking Modules

### Annotate $D^2_\text{min}$
The `annotate_D2min` module provides a process that calculates the
cell motility measure $D_\text{min}^2$. This measure quantifies non-affine
movements of cells with regard to their neighbors by optimizing the
strain tensor $\pmb{E}$:

$D^2_{\text{min}, i} = \text{min} \left[\frac{1}{N} \sum_{j \in \mathcal{N}_i} \left(\pmb{r}_{i,j}(t+T) - \pmb{E}_i \pmb{r}_{i,j}(t) \right) \right]$

Import the module into your pipeline script via

```nextflow
include { annotate_D2min } from './cellular-dynamics-nf-modules/modules/tracking/annotate_D2min/main.nf'
```

|Argument Index | Argument Name|Argument Type|Description|
|-|-|-|-|
|1||tuple(val, path)|(`basename`, `graph_dataset_fpath`)|
|2|`delta_t_minutes`|val|Floating point number defining the time ($\Delta t$) between two adjacent frames.|
|3|`lag-times_minutes`|val|String of comma-separated lag times (in minutes) the $D^2_\text{min}$ measure should be calculated for.|
|4|`mum_per_px`|val|Floating point number defining the image resolution in microns per pixel ($\frac{\mu m}{\text{px}}$)|
|5|`minimum_neighbors`|val|Integer defining the minimum number of successfully tracked neighbors needed for calculating $D^2_\text{min}$. This should always be `2` or more.|
|6|`parent_dir_out`|val|Directory to which the resulting file will be published.|

### Annotate Neighbor Retention
### Cell Tracking (Overlap Tracking)
### Assemble Cell Tracks DataFrame
### Concatenate Tracking DataFrames

This module combines the tracking dataframes from all processed datasets into a single big dataframe.
The cell track IDs are adjusted such that they remain unique in the dataframe.

#### Inputs:
|Argument Index | Argument Name|Argument Type|Description|
|-|-|-|-|
|1||val |```tracking_df_files_list```|  list of individual tracking dataframes' filepaths
|2|`parent_dir_out`|val|Directory to which the resulting file will be published.|

#### Outputs:
|Argument Index | Argument Name|Argument Type|Description|
|-|-|-|-|
|1||path |```"all_cell_tracks.ipc"```|  file path of concatenated dataframe

## Graph Processing Modules

### Structure Abstraction
### Build Graphs
### Annotate Graph Theoretical Observables

### Calculate Local Density

A cell's local density $\rho$ is defined to be the inverse of the mean
cell area $\bar{A}$ of the cell and its neighbors:

$\rho_i = \frac{1}{\bar{A}} = \frac{1}{\frac{1}{|\mathcal{N_i}| + 1} \left(A_i + \sum_{j \in \mathcal{N_i} }A_j\right)}$


```nextflow
include { calculate_local_density } from './cellular-dynamics-nf-modules/modules/graph_processing/calculate_local_density/main.nf'
```

#### Inputs:
|Argument Index | Argument Name|Argument Type|Description|
|-|-|-|-|
|1||tuple(val, path)|(`basename`, `fpath`)|
|2|`parent_dir_out`|val|Directory to which the resulting file will be published.|
