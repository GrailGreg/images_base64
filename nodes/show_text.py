class BaseNode():
    FUNCTION = "func"

class BaseNodeStringAssistant(BaseNode):
    CATEGORY = "Image base 64"

class ShowText64(BaseNodeStringAssistant): 
    RETURN_TYPES = ()
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {
                    "forceInput": True,
                    "default": ""
                }),
            },
        }
    def func(self, text=""):
        return {"ui": {"text": text}}
