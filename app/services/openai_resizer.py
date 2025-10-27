"""OpenAI Vision-powered intelligent image resizing service"""
import base64
import io
import logging
from typing import Optional, Tuple, Dict
from PIL import Image
import openai
from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIResizerService:
    """Service for intelligent image resizing using OpenAI Vision API"""

    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            logger.warning("OpenAI API key not configured. Intelligent resizing unavailable.")

    def analyze_image_composition(self, image: Image.Image) -> Optional[Dict]:
        """
        Analyze image composition using OpenAI Vision API
        Returns bounding box and composition info for intelligent cropping
        """
        if not self.client:
            return None

        try:
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=95)
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            # Prepare prompt for Vision API
            prompt = """Analyze this image and identify the main subject/focal point (e.g., product, person, food item).

Return ONLY a JSON object with this exact structure:
{
    "subject_bbox": {
        "x": <left position as decimal 0-1>,
        "y": <top position as decimal 0-1>,
        "width": <width as decimal 0-1>,
        "height": <height as decimal 0-1>
    },
    "subject_type": "<brief description like 'burger', 'person', 'product'>",
    "can_crop_top": <true/false - can we safely crop from top>,
    "can_crop_bottom": <true/false - can we safely crop from bottom>,
    "can_crop_left": <true/false - can we safely crop from left>,
    "can_crop_right": <true/false - can we safely crop from right>
}

The bbox should tightly fit the main subject. Use decimal coordinates where 0,0 is top-left and 1,1 is bottom-right.
Example: if burger is in center taking up 60% of image: {"x": 0.2, "y": 0.2, "width": 0.6, "height": 0.6}"""

            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model=settings.OPENAI_VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0.1
            )

            # Parse response
            content = response.choices[0].message.content

            # Extract JSON from response (handle code blocks)
            import json
            import re

            # Try to find JSON in code blocks first
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find raw JSON
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    logger.error("No JSON found in OpenAI response")
                    return None

            analysis = json.loads(json_str)
            logger.info(f"OpenAI Vision analysis: {analysis['subject_type']}")
            return analysis

        except Exception as e:
            logger.error(f"OpenAI Vision API error: {e}", exc_info=True)
            return None

    def calculate_smart_crop(
        self,
        image_size: Tuple[int, int],
        target_size: Tuple[int, int],
        analysis: Dict
    ) -> Tuple[int, int, int, int]:
        """
        Calculate optimal crop box based on Vision API analysis
        Returns (left, top, right, bottom) in pixels
        """
        img_width, img_height = image_size
        target_width, target_height = target_size
        target_aspect = target_width / target_height

        # Get subject bounding box
        bbox = analysis.get('subject_bbox', {})
        subject_x = bbox.get('x', 0.5)
        subject_y = bbox.get('y', 0.5)
        subject_w = bbox.get('width', 0.8)
        subject_h = bbox.get('height', 0.8)

        # Convert to pixel coordinates
        subject_left = int(subject_x * img_width)
        subject_top = int(subject_y * img_height)
        subject_right = int((subject_x + subject_w) * img_width)
        subject_bottom = int((subject_y + subject_h) * img_height)

        subject_center_x = (subject_left + subject_right) // 2
        subject_center_y = (subject_top + subject_bottom) // 2

        # Calculate crop dimensions based on target aspect ratio
        if target_aspect > img_width / img_height:
            # Target is wider than source - use full width
            crop_width = img_width
            crop_height = int(crop_width / target_aspect)
        else:
            # Target is taller than source - use full height
            crop_height = img_height
            crop_width = int(crop_height * target_aspect)

        # Ensure crop dimensions don't exceed image
        crop_width = min(crop_width, img_width)
        crop_height = min(crop_height, img_height)

        # Center crop around subject
        crop_left = subject_center_x - crop_width // 2
        crop_top = subject_center_y - crop_height // 2

        # Adjust if crop goes out of bounds
        if crop_left < 0:
            crop_left = 0
        elif crop_left + crop_width > img_width:
            crop_left = img_width - crop_width

        if crop_top < 0:
            crop_top = 0
        elif crop_top + crop_height > img_height:
            crop_top = img_height - crop_height

        crop_right = crop_left + crop_width
        crop_bottom = crop_top + crop_height

        return (crop_left, crop_top, crop_right, crop_bottom)

    def resize_intelligently(
        self,
        image: Image.Image,
        target_size: Tuple[int, int],
        analysis: Optional[Dict] = None
    ) -> Image.Image:
        """
        Resize image intelligently using Vision API analysis
        If no analysis provided, will call Vision API
        """
        # Get analysis if not provided
        if analysis is None:
            analysis = self.analyze_image_composition(image)

        # If no analysis available, fall back to basic crop-to-fill
        if analysis is None:
            return self._fallback_crop_to_fill(image, target_size)

        # Calculate smart crop
        crop_box = self.calculate_smart_crop(image.size, target_size, analysis)

        # Crop and resize
        cropped = image.crop(crop_box)
        resized = cropped.resize(target_size, Image.Resampling.LANCZOS)

        logger.info(f"Smart crop: {image.size} → crop{crop_box} → {target_size}")
        return resized

    def _fallback_crop_to_fill(self, image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """
        Fallback method: crop to fill without OpenAI analysis
        Centers the crop and fills the entire frame
        """
        img_width, img_height = image.size
        target_width, target_height = target_size

        img_aspect = img_width / img_height
        target_aspect = target_width / target_height

        if target_aspect > img_aspect:
            # Target is wider - crop height
            new_height = int(img_width / target_aspect)
            top = (img_height - new_height) // 2
            crop_box = (0, top, img_width, top + new_height)
        else:
            # Target is taller - crop width
            new_width = int(img_height * target_aspect)
            left = (img_width - new_width) // 2
            crop_box = (left, 0, left + new_width, img_height)

        cropped = image.crop(crop_box)
        resized = cropped.resize(target_size, Image.Resampling.LANCZOS)

        logger.info(f"Fallback crop: {image.size} → crop{crop_box} → {target_size}")
        return resized


# Global instance
openai_resizer = OpenAIResizerService()
