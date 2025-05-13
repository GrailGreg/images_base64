from .nodes.node_64 import SaveImage64
from .nodes.show_text import ShowText64

NODE_CLASS_MAPPINGS = {
    "SaveImage64": SaveImage64,
    "ShowText64": ShowText64, 
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImage64": "Save Image & Base64 Output",
    "ShowText64": "Base64 - Show & Copy Text", 
}

WEB_DIRECTORY = "js"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
