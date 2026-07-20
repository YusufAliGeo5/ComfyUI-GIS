# ComfyUI-GIS

Visual geospatial processing and GeoAI nodes for [ComfyUI](https://comfy.org/). Build custom reproducible GIS workflows for raster, vector, remote sensing, spatial analysis, and machine learning.

![ComfyUI-GIS teaser](./assets/ComfyUI-GIS-Banner.png)

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

## Available Nodes

### Inspect Vector Dataset

Reads vector metadata without modifying the source dataset. It reports:

- available layers
- driver and encoding
- feature count
- geometry type
- coordinate reference system
- dataset bounds
- attribute fields and data types

### Preview Vector Dataset

Renders a static visual preview of point, line, and polygon data as a standard ComfyUI `IMAGE`.

```text
Preview Vector Dataset → Preview Image
                       └→ Show Text (optional summary)
```

The preview automatically zooms to the layer extent, preserves the coordinate aspect ratio, supports dark and light themes, and can display the filename, layer, feature count, geometry type, and CRS. The source dataset is never edited.

For large layers, `max_features` limits how many features are drawn. The full dataset bounds are still used for the preview extent, and the preview clearly reports when the limit was reached.

## Initial Roadmap

- [x] Create the custom-node package structure
- [x] Add a minimal project-status node for installation testing
- [x] Register and execute the first ComfyUI-GIS node
- [x] Inspect vector dataset metadata with Pyogrio
- [x] Load vector geometry with GeoPandas
- [x] Add static vector preview generation
- [ ] Create a vector buffer
- [ ] Export the result to GeoPackage
- [ ] Add CRS validation and reprojection
- [ ] Add raster-loading nodes
- [ ] Add zonal statistics
- [ ] Explore GeoAI segmentation workflows
- [ ] Explore optional ArcPy integration

## Project Principles

- GIS data should retain its CRS and spatial metadata.
- Spatially invalid operations should produce clear errors.
- Core functionality should use open-source GIS libraries.
- ArcPy integration should remain optional.
- GIS processing logic should remain separate from ComfyUI-specific code.
- Workflows should be reproducible and inspectable.
- Preview nodes must never modify source data.

## Installation

1. Clone or extract the repository into:

   ```text
   ComfyUI/custom_nodes/ComfyUI-GIS
   ```

2. Install the dependencies using the exact Python executable that launches ComfyUI:

   ```powershell
   & "C:\path\to\ComfyUI\venv\Scripts\python.exe" -m pip install -r "C:\path\to\ComfyUI-GIS\requirements.txt"
   ```

   When using ComfyUI Portable with an embedded Python, replace the executable path with its `python_embeded\python.exe` path.

3. Restart ComfyUI completely.
4. Search under the `GIS` category for:

   - **ComfyUI-GIS Project Status**
   - **Inspect Vector Dataset**
   - **Preview Vector Dataset**

5. Connect the `preview` output of **Preview Vector Dataset** to ComfyUI's built-in **Preview Image** node.

## Cache and External File Edits

ComfyUI caches node results. The vector nodes fingerprint the dataset path, file size, and modification time so that a file edited externally in QGIS or ArcGIS is read again on the next queued run. Shapefile sidecar files such as `.dbf`, `.shx`, and `.prj` are included in this check.

## Author

ComfyUI-GIS was conceived and created by Yusuf Ali.

GitHub: [@YusufAliGeo5](https://github.com/YusufAliGeo5)

## Attribution

Copyright © 2026 Yusuf Ali.

Redistributions and modified versions must preserve the applicable copyright, license, and author-attribution notices.

## Disclaimer

ComfyUI-GIS is an independent community project. It is not affiliated with or endorsed by Comfy Org, Esri, Meta, or other third-party software and model providers referenced by the project.
Third-party software, models, APIs, and datasets remain subject to their respective licenses and terms.

## License

Licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE).
