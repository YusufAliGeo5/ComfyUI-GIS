class ComfyUIGISProjectStatus:
    """Simple output node used to verify that ComfyUI-GIS executes."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)

    FUNCTION = "run"
    CATEGORY = "GIS/Development"

    # This makes the node a valid endpoint for workflow execution.
    OUTPUT_NODE = True

    def run(self):
        message = "ComfyUI-GIS executed successfully."
        print(f"[ComfyUI-GIS] {message}")
        return (message,)