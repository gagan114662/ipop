# app/utils/layout_adapter.py
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Dict
from app.utils.layout_detector import LayoutElement, layout_detector
from app.utils.platform_configs import PlatformSpec
import logging

logger = logging.getLogger(__name__)

class LayoutAdapter:
    def __init__(self):
        self.layout_rules = self._initialize_layout_rules()
    
    def _initialize_layout_rules(self) -> Dict[str, Dict]:
        """Define layout rules for different platform types"""
        return {
            'square': {  # Instagram Feed, etc.
                'product_placement': 'center',
                'text_placement': 'bottom',
                'logo_placement': 'top_right',
                'price_placement': 'bottom_right'
            },
            'story': {  # Instagram Story, etc.
                'product_placement': 'center_right',
                'text_placement': 'top',
                'logo_placement': 'top_left',
                'price_placement': 'bottom_center'
            },
            'banner': {  # Google Display, etc.
                'product_placement': 'left',
                'text_placement': 'right',
                'logo_placement': 'bottom_right',
                'price_placement': 'right_center'
            }
        }
    
    def get_layout_type(self, platform_spec: PlatformSpec) -> str:
        """Determine layout type based on platform dimensions"""
        width, height = platform_spec.dimensions
        aspect_ratio = width / height
        
        if 0.9 <= aspect_ratio <= 1.1:
            return 'square'
        elif aspect_ratio < 0.7:  # Tall
            return 'story'
        elif aspect_ratio > 1.4:  # Wide
            return 'banner'
        else:
            return 'square'  # Default
    
    def adapt_layout(self, image: Image.Image, elements: List[LayoutElement], 
                    platform_spec: PlatformSpec) -> Image.Image:
        """Adapt creative layout to new platform dimensions"""
        try:
            # Convert PIL to OpenCV
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Get target dimensions and layout type
            target_width, target_height = platform_spec.dimensions
            layout_type = self.get_layout_type(platform_spec)
            layout_rules = self.layout_rules[layout_type]
            
            # Create blank canvas
            canvas = np.ones((target_height, target_width, 3), dtype=np.uint8) * 255  # White background
            
            # Calculate scaling factor
            orig_height, orig_width = opencv_image.shape[:2]
            scale_x = target_width / orig_width
            scale_y = target_height / orig_height
            scale = min(scale_x, scale_y)
            
            # Resize original image to fit
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
            resized_original = cv2.resize(opencv_image, (new_width, new_height))
            
            # Position resized image on canvas
            x_offset = (target_width - new_width) // 2
            y_offset = (target_height - new_height) // 2
            canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized_original
            
            # Reposition elements according to layout rules
            canvas = self._reposition_elements(
                canvas, elements, layout_rules, 
                scale, (x_offset, y_offset),
                (target_width, target_height)
            )
            
            # Convert back to PIL
            result_image = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
            return result_image
            
        except Exception as e:
            logger.error(f"Layout adaptation failed: {e}")
            # Fallback: basic resize
            return image.resize(platform_spec.dimensions, Image.Resampling.LANCZOS)
    
    def _reposition_elements(self, canvas: np.ndarray, elements: List[LayoutElement],
                           layout_rules: Dict, scale: float, offset: Tuple[int, int],
                           target_size: Tuple[int, int]) -> np.ndarray:
        """Reposition elements according to layout rules"""
        target_width, target_height = target_size
        x_offset, y_offset = offset
        
        for element in elements[:6]:  # Process top 6 most important elements
            try:
                # Scale element position and size
                x1, y1, x2, y2 = element.bbox
                scaled_x1 = int(x1 * scale) + x_offset
                scaled_y1 = int(y1 * scale) + y_offset
                scaled_x2 = int(x2 * scale) + x_offset
                scaled_y2 = int(y2 * scale) + y_offset
                
                # Get new position based on layout rules
                new_bbox = self._calculate_new_position(
                    element.type, (scaled_x1, scaled_y1, scaled_x2, scaled_y2),
                    layout_rules, target_size, element.area * scale * scale
                )
                
                # Extract element from original position
                element_region = canvas[scaled_y1:scaled_y2, scaled_x1:scaled_x2]
                
                # Place element in new position
                new_x1, new_y1, new_x2, new_y2 = new_bbox
                canvas[new_y1:new_y2, new_x1:new_x2] = element_region
                
                # Fill original position with background
                canvas[scaled_y1:scaled_y2, scaled_x1:scaled_x2] = 255  # White
                
            except Exception as e:
                logger.warning(f"Could not reposition {element.type}: {e}")
                continue
        
        return canvas
    
    def _calculate_new_position(self, element_type: str, original_bbox: Tuple[int, int, int, int],
                              layout_rules: Dict, target_size: Tuple[int, int], 
                              element_area: float) -> Tuple[int, int, int, int]:
        """Calculate new position for element based on layout rules"""
        target_width, target_height = target_size
        x1, y1, x2, y2 = original_bbox
        element_width = x2 - x1
        element_height = y2 - y1
        
        placement_rule = layout_rules.get(f'{element_type}_placement', 'center')
        
        # Define position mappings
        positions = {
            'center': (target_width//2 - element_width//2, target_height//2 - element_height//2),
            'top': (target_width//2 - element_width//2, 20),
            'bottom': (target_width//2 - element_width//2, target_height - element_height - 20),
            'left': (20, target_height//2 - element_height//2),
            'right': (target_width - element_width - 20, target_height//2 - element_height//2),
            'top_left': (20, 20),
            'top_right': (target_width - element_width - 20, 20),
            'bottom_left': (20, target_height - element_height - 20),
            'bottom_right': (target_width - element_width - 20, target_height - element_height - 20),
            'center_right': (target_width - element_width - 50, target_height//2 - element_height//2),
            'center_left': (50, target_height//2 - element_height//2),
            'bottom_center': (target_width//2 - element_width//2, target_height - element_height - 50)
        }
        
        new_x, new_y = positions.get(placement_rule, (target_width//2, target_height//2))
        
        return (new_x, new_y, new_x + element_width, new_y + element_height)

# Global adapter instance
layout_adapter = LayoutAdapter()