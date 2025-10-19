# app/utils/layout_detector.py
import cv2
import numpy as np
from PIL import Image, ImageDraw
from ultralytics import YOLO
import pytesseract
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class LayoutElement:
    def __init__(self, element_type: str, bbox: Tuple[int, int, int, int], 
                 confidence: float, content: Optional[str] = None):
        self.type = element_type
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.confidence = confidence
        self.content = content
        self.importance = self._calculate_importance()
    
    def _calculate_importance(self) -> int:
        """Calculate element importance for layout decisions"""
        importance_map = {
            'person': 100,
            'product': 90,
            'logo': 80,
            'text': 70,
            'price': 85,
            'headline': 75,
            'button': 60,
            'background': 10
        }
        return importance_map.get(self.type, 50)
    
    @property
    def center(self) -> Tuple[int, int]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    @property
    def area(self) -> int:
        x1, y1, x2, y2 = self.bbox
        return (x2 - x1) * (y2 - y1)

class CreativeLayoutDetector:
    def __init__(self):
        # Load YOLO models for different element types
        try:
            self.object_detector = YOLO("yolov8n.pt")  # General objects
            self.logo_detector = YOLO("yolov8n.pt")    # Could use custom logo model
        except:
            logger.warning("YOLO models not available, using fallback detection")
            self.object_detector = None
            self.logo_detector = None
    
    def detect_elements(self, image: np.ndarray) -> List[LayoutElement]:
        """Detect all creative elements in image"""
        elements = []
        
        # Detect objects with YOLO
        if self.object_detector:
            elements.extend(self._detect_objects(image))
        
        # Detect text regions
        elements.extend(self._detect_text_regions(image))
        
        # Detect logos (simplified)
        elements.extend(self._detect_logos(image))
        
        # Detect prices and special elements
        elements.extend(self._detect_special_elements(image))
        
        return self._filter_and_rank_elements(elements)
    
    def _detect_objects(self, image: np.ndarray) -> List[LayoutElement]:
        """Detect general objects using YOLO"""
        elements = []
        try:
            results = self.object_detector(image)
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        cls = int(box.cls[0].cpu().numpy())
                        
                        class_name = self.object_detector.names[cls]
                        
                        # Map YOLO classes to our creative elements
                        creative_type = self._map_yolo_to_creative(class_name)
                        
                        if creative_type:
                            elements.append(LayoutElement(
                                element_type=creative_type,
                                bbox=(int(x1), int(y1), int(x2), int(y2)),
                                confidence=float(conf)
                            ))
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
        
        return elements
    
    def _map_yolo_to_creative(self, yolo_class: str) -> Optional[str]:
        """Map YOLO object classes to creative element types"""
        mapping = {
            'person': 'person',
            'cell phone': 'product',
            'laptop': 'product',
            'bottle': 'product',
            'cup': 'product',
            'handbag': 'product',
            'tie': 'product',
            'sports ball': 'product',
            'book': 'product',
            'tv': 'product',
            'remote': 'product'
        }
        return mapping.get(yolo_class)
    
    def _detect_text_regions(self, image: np.ndarray) -> List[LayoutElement]:
        """Detect text regions using OCR and contour detection"""
        elements = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Use OCR to detect text and its bounding boxes
            ocr_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            for i in range(len(ocr_data['text'])):
                if ocr_data['text'][i].strip():  # Non-empty text
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    conf = ocr_data['conf'][i] / 100.0  # Normalize to 0-1
                    
                    text_content = ocr_data['text'][i].strip()
                    
                    # Determine text type
                    text_type = self._classify_text_type(text_content)
                    
                    elements.append(LayoutElement(
                        element_type=text_type,
                        bbox=(x, y, x + w, y + h),
                        confidence=conf,
                        content=text_content
                    ))
        except Exception as e:
            logger.error(f"Text detection failed: {e}")
        
        return elements
    
    def _classify_text_type(self, text: str) -> str:
        """Classify text into specific types"""
        text_lower = text.lower()
        
        # Price detection
        if any(char in text for char in ['$', '€', '£', '₹']) or (
            any(word in text_lower for word in ['price', 'only', 'save', 'off', '%'])
        ):
            return 'price'
        
        # Headline detection (usually shorter, impactful)
        if len(text.split()) <= 8 and any(c.isupper() for c in text):
            return 'headline'
        
        # Button detection
        if any(word in text_lower for word in ['buy', 'shop', 'order', 'click', 'learn', 'more']):
            return 'button'
        
        return 'text'
    
    def _detect_logos(self, image: np.ndarray) -> List[LayoutElement]:
        """Detect logo-like regions"""
        elements = []
        
        try:
            # Simple logo detection using feature matching or contour analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Find contours that might be logos (small, compact regions)
            _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 1000 > area > 100:  # Reasonable logo size range
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Check if it looks like a logo (compact shape)
                    aspect_ratio = w / h
                    if 0.3 < aspect_ratio < 3.0:  # Reasonable aspect ratios
                        elements.append(LayoutElement(
                            element_type='logo',
                            bbox=(x, y, x + w, y + h),
                            confidence=0.7  # Moderate confidence
                        ))
        except Exception as e:
            logger.error(f"Logo detection failed: {e}")
        
        return elements
    
    def _detect_special_elements(self, image: np.ndarray) -> List[LayoutElement]:
        """Detect special elements like prices using pattern matching"""
        elements = []
        
        try:
            # Look for price patterns in the image
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhanced text detection for prices
            ocr_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                if any(char in text for char in ['$', '€', '£', '₹']):
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    
                    elements.append(LayoutElement(
                        element_type='price',
                        bbox=(x, y, x + w, y + h),
                        confidence=0.9,
                        content=text
                    ))
        except Exception as e:
            logger.error(f"Special element detection failed: {e}")
        
        return elements
    
    def _filter_and_rank_elements(self, elements: List[LayoutElement]) -> List[LayoutElement]:
        """Filter and rank elements by importance and confidence"""
        # Remove duplicates and low-confidence elements
        filtered = []
        seen_areas = set()
        
        for element in elements:
            area_key = (element.bbox[0] // 10, element.bbox[1] // 10, 
                       element.bbox[2] // 10, element.bbox[3] // 10)
            
            if element.confidence > 0.3 and area_key not in seen_areas:
                filtered.append(element)
                seen_areas.add(area_key)
        
        # Sort by importance (highest first)
        return sorted(filtered, key=lambda x: x.importance, reverse=True)

# Global detector instance
layout_detector = CreativeLayoutDetector()