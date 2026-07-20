"""ComfyUI node for rendering a static vector dataset preview."""

from __future__ import annotations

from ..core.vector_info import vector_dataset_fingerprint
from ..core.vector_preview import render_vector_preview


class ComfyUIGISPreviewVector:
    """Render point, line, and polygon data as a standard ComfyUI image."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "vector_path": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "placeholder": r"C:\data\ottawa_boundary.gpkg",
                    },
                ),
                "layer": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "placeholder": "Leave blank to use the first layer",
                    },
                ),
                "width": (
                    "INT",
                    {"default": 1024, "min": 256, "max": 2048, "step": 64},
                ),
                "height": (
                    "INT",
                    {"default": 768, "min": 256, "max": 2048, "step": 64},
                ),
                "max_features": (
                    "INT",
                    {
                        "default": 25000,
                        "min": 100,
                        "max": 1000000,
                        "step": 100,
                    },
                ),
                "theme": (["dark", "light"], {"default": "dark"}),
                "show_metadata": ("BOOLEAN", {"default": True}),
                "show_axes": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("preview", "summary")
    FUNCTION = "preview"
    CATEGORY = "GIS/Vector"
    OUTPUT_NODE = True
    DESCRIPTION = (
        "Creates a static preview of a vector layer without modifying the source. "
        "Connect the preview output to ComfyUI's built-in Preview Image node."
    )
    SEARCH_ALIASES = [
        "view shapefile",
        "preview geopackage",
        "view vector",
        "map preview",
        "preview points",
        "preview polygons",
        "preview lines",
    ]

    @classmethod
    def IS_CHANGED(
        cls,
        vector_path: str,
        layer: str = "",
        width: int = 1024,
        height: int = 768,
        max_features: int = 25000,
        theme: str = "dark",
        show_metadata: bool = True,
        show_axes: bool = False,
    ):
        return vector_dataset_fingerprint(
            vector_path=vector_path,
            layer=layer,
            extra=(
                width,
                height,
                max_features,
                theme,
                show_metadata,
                show_axes,
            ),
        )

    def preview(
        self,
        vector_path: str,
        layer: str = "",
        width: int = 1024,
        height: int = 768,
        max_features: int = 25000,
        theme: str = "dark",
        show_metadata: bool = True,
        show_axes: bool = False,
    ):
        image, summary = render_vector_preview(
            vector_path=vector_path,
            layer=layer,
            width=width,
            height=height,
            max_features=max_features,
            theme=theme,
            show_metadata=show_metadata,
            show_axes=show_axes,
        )

        print(f"\n[ComfyUI-GIS]\n{summary}\n")
        return {
            "ui": {"text": [summary]},
            "result": (image, summary),
        }
