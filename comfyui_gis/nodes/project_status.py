class ComfyUIGISProjectStatus:
    """Output node used to verify that ComfyUI-GIS executes correctly."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {}
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)

    FUNCTION = "run"
    CATEGORY = "GIS/Development"

    # Marks this node as a workflow endpoint.
    OUTPUT_NODE = True

    def run(self):
        message = "ComfyUI-GIS executed successfully."
        print(f"[ComfyUI-GIS] {message}")

        return {
            "ui": {
                "text": [message]
            },
            "result": (message,)
        }