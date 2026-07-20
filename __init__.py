"""ComfyUI-GIS custom node package.

Copyright (c) 2026 Yusuf Ali
Licensed under the GNU General Public License v3.0.
"""

from .comfyui_gis.nodes.project_status import ComfyUIGISProjectStatus
from .comfyui_gis.nodes.vector_inspect import ComfyUIGISInspectVector
from .comfyui_gis.nodes.vector_preview import ComfyUIGISPreviewVector

NODE_CLASS_MAPPINGS = {
    "YAGIS_ProjectStatus": ComfyUIGISProjectStatus,
    "YAGIS_InspectVector": ComfyUIGISInspectVector,
    "YAGIS_PreviewVector": ComfyUIGISPreviewVector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YAGIS_ProjectStatus": "ComfyUI-GIS Project Status",
    "YAGIS_InspectVector": "Inspect Vector Dataset",
    "YAGIS_PreviewVector": "Preview Vector Dataset",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
