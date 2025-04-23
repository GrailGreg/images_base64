import folder_paths, random, json, os, io, base64
from .cli_args import args
from PIL import Image
import numpy as np
from PIL.PngImagePlugin import PngInfo

class BaseSaveImage64:
    def __init__(self, output_type='output'):
            self.type = output_type
            self.compress_level = 4
            self.prefix_append = ''

            if output_type == 'output':
                    self.output_dir = folder_paths.get_output_directory()
            else:
                    self.output_dir = folder_paths.get_temp_directory()
                    self.prefix_append = '_temp_' + ''.join(random.choice('abcdefghijklmnopqrstupvxyz') for x in range(5))

    def save_images(self, images, filename_prefix='ComfyUI', prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, _ = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0]
        )
        results = []
        base64_strings = []

        for batch_number, image in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            # ===== FIXED METADATA HANDLING =====
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text('prompt', json.dumps(prompt))
                if extra_pnginfo is not None:
                    # Handle list-wrapped format used by ComfyUI
                    if isinstance(extra_pnginfo, list) and len(extra_pnginfo) > 0:
                        workflow_meta = extra_pnginfo[0]
                        if isinstance(workflow_meta, dict):
                            for key in workflow_meta:
                                metadata.add_text(key, json.dumps(workflow_meta[key]))
                        else:
                            print(f"Warning: extra_pnginfo[0] is {type(workflow_meta)}, expected dict")
                    else:
                        print(f"Warning: extra_pnginfo is {type(extra_pnginfo)}, expected list")
            # ===== END FIX =====

            filename_with_batch = filename.replace('%batch_num%', str(batch_number))
            file = f'{filename_with_batch}_{counter:05}_.png'
            img.save(
                os.path.join(full_output_folder, file),
                pnginfo=metadata,
                compress_level=self.compress_level
            )

            buffer = io.BytesIO()
            img.save(buffer, format='PNG', pnginfo=metadata, compress_level=self.compress_level)
            base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            base64_strings.append(base64_str)

            results.append({
                'filename': file,
                'subfolder': subfolder,
                'type': self.type
            })
            counter += 1

        return results, base64_strings
    
class SaveImage64(BaseSaveImage64):
    def __init__(self):
        super().__init__(output_type='output')

    @classmethod
    def INPUT_TYPES(s):
        return {
            'required': {
                'images': ('IMAGE', {'tooltip': 'The images to save.'}),
                'filename_prefix': ('STRING', {'default': 'ComfyUI'}),
            },
            'hidden': {'prompt': 'PROMPT', 'extra_pnginfo': 'EXTRA_PNGINFO'},
        }

    RETURN_TYPES = ('STRING',)
    RETURN_NAMES = ('base64',)
    FUNCTION = 'save_images'  # Matches method name
    OUTPUT_NODE = True
    CATEGORY = 'image'

    def save_images(self, images, filename_prefix='ComfyUI', prompt=None, extra_pnginfo=None):
            results, base64_strings = super().save_images(images, filename_prefix, prompt, extra_pnginfo)
            
            # Return the first base64 string if there's only one image
            if len(base64_strings) == 1:
                    return (base64_strings[0],), {'ui': {'images': results}}
            # For multiple images, join with commas (or return as list)
            else:
                    return (','.join(base64_strings),), {'ui': {'images': results}}

class PreviewImage64(BaseSaveImage64):
    def __init__(self):
        super().__init__(output_type='temp')

    @classmethod
    def INPUT_TYPES(s):
        return {
            'required': {'images': ('IMAGE',)},
            'hidden': {'prompt': 'PROMPT', 'extra_pnginfo': 'EXTRA_PNGINFO'},
        }

    RETURN_TYPES = ()
    FUNCTION = 'save_images'  # Matches method name
    OUTPUT_NODE = True
    CATEGORY = 'image'

    def save_images(self, images, filename_prefix='ComfyUI', prompt=None, extra_pnginfo=None):
        results, _ = super().save_images(images, filename_prefix, prompt, extra_pnginfo)
        # Correct return format: (outputs, ui_data)
        return (), {'ui': {'images': results}}