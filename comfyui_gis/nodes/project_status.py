"""Minimal validation node used to confirm that ComfyUI-GIS loads correctly."""


class ComfyUIGISProjectStatus:
    """Return a simple status message without requiring GIS dependencies."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "message": (
                    "STRING",
                    {
                        "default": "ComfyUI-GIS is installed and ready for development.",
                        "multiline": True,
                    },
                )
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "run"
    CATEGORY = "ComfyUI-GIS/Development"
    DESCRIPTION = "Confirms that the ComfyUI-GIS custom-node package loads successfully."

    def run(self, message: str):
        text = message.strip() or "ComfyUI-GIS loaded successfully."
        print(f"[ComfyUI-GIS] {text}")
        return (text,)
