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
|Argument Name|Argument Type|Description|
|-|-|-|
||||

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

|Argument Name|Argument Type|Description|
|-|-|-|
||||

### Annotate Neighbor Retention
### Cell Tracking (Overlap Tracking)
### Assemble Cell Tracks DataFrame

## Graph Processing Modules

### Structure Abstraction
### Build Graphs
### Annotate Graph Theoretical Observables

