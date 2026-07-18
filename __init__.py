"""ComfyUI-GIS custom node package.

Copyright (c) 2026 Yusuf Ali
Licensed under the GNU General Public License v3.0.
"""

from .comfyui_gis.nodes.project_status import ComfyUIGISProjectStatus

NODE_CLASS_MAPPINGS = {
    "YAGIS_ProjectStatus": ComfyUIGISProjectStatus,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YAGIS_ProjectStatus": "ComfyUI-GIS Project Status",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
