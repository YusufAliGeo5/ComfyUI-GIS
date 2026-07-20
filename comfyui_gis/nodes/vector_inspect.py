"""ComfyUI node for inspecting vector dataset metadata."""

from ..core.vector_info import inspect_vector_dataset, vector_dataset_fingerprint


class ComfyUIGISInspectVector:
    """Inspect a vector dataset without changing it."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "vector_path": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "placeholder": r"C:\data\roads.gpkg",
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
                "force_exact_metadata": (
                    "BOOLEAN",
                    {"default": False},
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("report",)
    FUNCTION = "inspect"
    CATEGORY = "GIS/Vector"
    OUTPUT_NODE = True
    DESCRIPTION = (
        "Reads vector metadata such as layers, feature count, geometry type, "
        "CRS, bounds, and attribute fields. The input dataset is not modified."
    )
    SEARCH_ALIASES = ["vector info", "inspect shapefile", "inspect geopackage"]

    @classmethod
    def IS_CHANGED(
        cls,
        vector_path: str,
        layer: str = "",
        force_exact_metadata: bool = False,
    ):
        return vector_dataset_fingerprint(
            vector_path=vector_path,
            layer=layer,
            extra=(force_exact_metadata,),
        )

    def inspect(
        self,
        vector_path: str,
        layer: str = "",
        force_exact_metadata: bool = False,
    ):
        report = inspect_vector_dataset(
            vector_path=vector_path,
            layer=layer,
            force_exact_metadata=force_exact_metadata,
        )

        print(f"\n[ComfyUI-GIS]\n{report}\n")
        return {
            "ui": {"text": [report]},
            "result": (report,),
        }
