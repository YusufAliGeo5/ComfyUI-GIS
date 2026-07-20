# Example Workflows

Example workflow JSON files will be added as nodes stabilize.

## Vector Preview

Create this graph manually in ComfyUI:

```text
Preview Vector Dataset ── preview ──→ Preview Image
                       └─ summary ──→ Show Text (optional)
```

Enter the local path to a GeoJSON, GeoPackage, Shapefile, FlatGeobuf, or another vector format supported by the installed GDAL/OGR drivers. Leave `layer` blank to use the first available layer.
