# ComfyUI-GIS

Visual geospatial processing and GeoAI nodes for [ComfyUI](https://comfy.org/). Build custom reproducible GIS workflows for raster, vector, remote sensing, spatial analysis, and machine learning.

![ComfyUI-GIS teaser](./ComfyUI-GIS-Banner.png)

> [!IMPORTANT]
> **Project status: Early development**
>
> ComfyUI-GIS is currently in early development. APIs, node names, dependencies, and workflow formats may change during development.

## Vision

ComfyUI-GIS aims to bring visual, node-based geospatial processing into ComfyUI.

The project will explore workflows combining:

- vector and raster geoprocessing
- remote-sensing imagery
- spatial analysis
- GeoAI and machine learning
- reproducible visual workflows
- optional integration with ArcPy and other GIS engines

## Initial Roadmap
 
- Create the custom-node package structure
- Register the first node in ComfyUI
- Load vector data with GeoPandas
- Create a vector buffer
- Export the result to GeoPackage
- Add CRS validation
- Add vector preview generation
- Add raster-loading nodes
- Add zonal statistics
- Explore GeoAI segmentation workflows
- Explore optional ArcPy integration

## Project Principles

- GIS data should retain its CRS and spatial metadata.
- Spatially invalid operations should produce clear errors.
- Core functionality should use open-source GIS libraries.
- ArcPy integration should remain optional.
- GIS processing logic should remain separate from ComfyUI-specific code.
- Workflows should be reproducible and inspectable.

## Installation

Installation instructions will be added after the first working node is available.

## Author

ComfyUI-GIS was conceived and created by Yusuf Ali.

GitHub: @YusufAliGeo5

## Attribution

Copyright © 2026 Yusuf Ali.

Redistributions and modified versions must preserve the applicable copyright, license, and author-attribution notices.

## Disclaimer

ComfyUI-GIS is an independent community project. It is not affiliated with or endorsed by Comfy Org, Esri, Meta, or other third-party software and model providers referenced by the project.
Third-party software, models, APIs, and datasets remain subject to their respective licenses and terms.

## License

Licensed under the GNU General Public License v3.0. See LICENSE.
