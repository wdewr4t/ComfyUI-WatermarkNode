import torch
import numpy as np
from PIL import Image

class WatermarkNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "watermark": ("IMAGE",),
                "tiles_per_row": ("INT", {"default": 3, "min": 1, "max": 20, "step": 1}),
                "opacity": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
                "overlap": ("FLOAT", {"default": 0.2, "min": -0.5, "max": 0.8, "step": 0.05}),
                "invert_mask": ("BOOLEAN", {"default": False}),  # 透明底变黑就勾选
            },
            "optional": {
                "watermark_mask": ("MASK",),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_watermark"
    CATEGORY = "image/processing"
    
    def apply_watermark(self, image, watermark, tiles_per_row, opacity, overlap, invert_mask, watermark_mask=None):
        img_batch = []
        
        for i in range(image.shape[0]):
            img_np = (image[i].cpu().numpy() * 255).astype(np.uint8)
            img_pil = Image.fromarray(img_np).convert("RGBA")
            img_w, img_h = img_pil.size
            
            wm_np = (watermark[0].cpu().numpy() * 255).astype(np.uint8)
            
            if wm_np.shape[-1] == 4:
                wm_pil = Image.fromarray(wm_np, mode='RGBA')
            else:
                wm_rgb = Image.fromarray(wm_np).convert("RGBA")
                
                if watermark_mask is not None:
                    mask_np = (watermark_mask[0].cpu().numpy() * 255).astype(np.uint8)
                    if len(mask_np.shape) == 3:
                        mask_np = mask_np[0]
                    
                    if invert_mask:
                        mask_np = 255 - mask_np
                    
                    alpha = Image.fromarray(mask_np, mode='L')
                    alpha = alpha.resize(wm_rgb.size, Image.Resampling.LANCZOS)
                    wm_pil = wm_rgb.copy()
                    wm_pil.putalpha(alpha)
                else:
                    wm_pil = wm_rgb
            
            wm_w, wm_h = wm_pil.size
            
            target_wm_width = int(img_w / (tiles_per_row * (1 - overlap)))
            target_wm_height = int(wm_h * (target_wm_width / wm_w))
            wm_pil = wm_pil.resize((target_wm_width, target_wm_height), Image.Resampling.LANCZOS)
            
            if opacity < 1.0:
                r, g, b, a = wm_pil.split()
                a = a.point(lambda p: int(p * opacity))
                wm_pil = Image.merge('RGBA', (r, g, b, a))
            
            step_x = int(target_wm_width * (1 - overlap))
            step_y = int(target_wm_height * (1 - overlap))
            tiled = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
            
            y = 0
            while y < img_h:
                x = 0
                while x < img_w:
                    tiled.paste(wm_pil, (x, y), wm_pil)
                    x += step_x
                y += step_y
            
            result = Image.alpha_composite(img_pil, tiled).convert("RGB")
            result_np = np.array(result).astype(np.float32) / 255.0
            img_batch.append(result_np)
        
        return (torch.from_numpy(np.stack(img_batch)),)


NODE_CLASS_MAPPINGS = {"WatermarkNode": WatermarkNode}
NODE_DISPLAY_NAME_MAPPINGS = {"WatermarkNode": "Add Watermark (Auto Tiled)"}