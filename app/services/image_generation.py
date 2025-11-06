"""
AI-Powered Image Generation Service
Integrates with DALL-E, Midjourney, and other image generation APIs
"""

from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
import openai
import os
import httpx
from enum import Enum


class ImageProvider(str, Enum):
    """Supported image generation providers"""
    DALLE3 = "dalle3"
    DALLE2 = "dalle2"
    STABLE_DIFFUSION = "stable_diffusion"
    MIDJOURNEY = "midjourney"  # Via API wrapper


class ImageStyle(str, Enum):
    """Image style presets"""
    NATURAL = "natural"
    VIVID = "vivid"
    CINEMATIC = "cinematic"
    MINIMALIST = "minimalist"
    ARTISTIC = "artistic"
    PHOTOGRAPHIC = "photographic"
    ILLUSTRATIVE = "illustrative"


class ImageQuality(str, Enum):
    """Image quality levels"""
    STANDARD = "standard"
    HD = "hd"
    ULTRA = "ultra"


class ImageSize(str, Enum):
    """Standard ad image sizes"""
    SQUARE_1080 = "1080x1080"  # Instagram/Facebook square
    LANDSCAPE_1200 = "1200x628"  # Facebook feed
    PORTRAIT_1080 = "1080x1920"  # Instagram story
    WIDE_1200 = "1200x900"  # Display ads
    DALLE_SQUARE = "1024x1024"  # DALL-E 3 square
    DALLE_LANDSCAPE = "1792x1024"  # DALL-E 3 landscape
    DALLE_PORTRAIT = "1024x1792"  # DALL-E 3 portrait


class GeneratedImage(BaseModel):
    """Generated image result"""
    url: str = Field(description="Temporary URL to generated image")
    permanent_url: Optional[str] = Field(None, description="Permanent CDN URL after upload")
    prompt: str = Field(description="Prompt used to generate")
    revised_prompt: Optional[str] = Field(None, description="Provider's revised prompt")
    provider: ImageProvider
    style: ImageStyle
    size: str
    quality: ImageQuality
    generation_time: float = Field(description="Time taken in seconds")
    quality_score: float = Field(description="Estimated quality 0-100")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ImageGenerationService:
    """
    Multi-provider image generation service
    Creates award-winning quality visuals for ad creatives
    """

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.default_provider = ImageProvider.DALLE3

        # Award-winning visual principles
        self.visual_principles = {
            "storytelling": [
                "Show a moment, not just a product",
                "Include human element or emotion",
                "Create narrative tension or resolution",
                "Evoke curiosity or aspiration"
            ],
            "composition": [
                "Rule of thirds",
                "Leading lines to focal point",
                "Balanced negative space",
                "Clear visual hierarchy"
            ],
            "emotional_impact": [
                "Authentic expressions and scenarios",
                "Relatable situations",
                "Aspirational yet achievable",
                "Cultural resonance"
            ],
            "technical_excellence": [
                "Professional lighting",
                "Sharp focus on key elements",
                "Color harmony and brand alignment",
                "High production value feel"
            ]
        }

    async def generate_ad_image(
        self,
        prompt: str,
        style: ImageStyle = ImageStyle.NATURAL,
        size: ImageSize = ImageSize.DALLE_SQUARE,
        quality: ImageQuality = ImageQuality.HD,
        provider: Optional[ImageProvider] = None,
        enhance_prompt: bool = True,
        brand_colors: Optional[List[str]] = None
    ) -> GeneratedImage:
        """
        Generate a single ad image

        Args:
            prompt: Base image prompt
            style: Visual style preference
            size: Image dimensions
            quality: Quality level
            provider: Image generation provider (defaults to DALL-E 3)
            enhance_prompt: Whether to enhance prompt with best practices
            brand_colors: Optional brand colors to incorporate

        Returns:
            Generated image with metadata
        """

        provider = provider or self.default_provider

        # Enhance prompt for award-winning quality
        if enhance_prompt:
            prompt = self._enhance_prompt(prompt, style, brand_colors)

        # Generate based on provider
        if provider == ImageProvider.DALLE3:
            return await self._generate_dalle3(prompt, size, quality, style)
        elif provider == ImageProvider.DALLE2:
            return await self._generate_dalle2(prompt, size)
        else:
            raise NotImplementedError(f"Provider {provider} not yet implemented")

    def _enhance_prompt(
        self,
        base_prompt: str,
        style: ImageStyle,
        brand_colors: Optional[List[str]] = None
    ) -> str:
        """
        Enhance prompt with award-winning visual principles
        """

        enhancements = []

        # Add style-specific enhancements
        style_enhancements = {
            ImageStyle.NATURAL: "natural lighting, authentic feel, realistic photography",
            ImageStyle.VIVID: "vibrant colors, high contrast, bold composition, dramatic lighting",
            ImageStyle.CINEMATIC: "cinematic lighting, shallow depth of field, film grain, professional color grading",
            ImageStyle.MINIMALIST: "clean composition, negative space, simple elegant design, minimal color palette",
            ImageStyle.ARTISTIC: "artistic interpretation, creative composition, unique perspective, painterly quality",
            ImageStyle.PHOTOGRAPHIC: "professional photography, studio quality, perfect lighting, sharp focus",
            ImageStyle.ILLUSTRATIVE: "illustrated style, graphic design elements, stylized composition"
        }

        enhancements.append(style_enhancements.get(style, ""))

        # Add quality markers
        quality_markers = [
            "award-winning photography",
            "professional composition",
            "high production value",
            "advertising campaign quality"
        ]
        enhancements.append(", ".join(quality_markers))

        # Add brand colors if provided
        if brand_colors:
            color_instruction = f"color palette featuring {', '.join(brand_colors)}"
            enhancements.append(color_instruction)

        # Combine
        enhanced = f"{base_prompt}, {', '.join(enhancements)}"

        # Ensure prompt isn't too long (DALL-E has 4000 char limit)
        if len(enhanced) > 3500:
            enhanced = enhanced[:3500]

        return enhanced

    async def _generate_dalle3(
        self,
        prompt: str,
        size: ImageSize,
        quality: ImageQuality,
        style: ImageStyle
    ) -> GeneratedImage:
        """Generate image using DALL-E 3"""

        start_time = datetime.now()

        # Map to DALL-E 3 parameters
        dalle_size = self._map_to_dalle_size(size)
        dalle_quality = "hd" if quality == ImageQuality.HD else "standard"
        dalle_style = "vivid" if style == ImageStyle.VIVID else "natural"

        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=dalle_size,
                quality=dalle_quality,
                style=dalle_style,
                n=1
            )

            generation_time = (datetime.now() - start_time).total_seconds()

            image_data = response.data[0]

            # Score quality
            quality_score = self._estimate_quality_score(
                prompt=prompt,
                provider=ImageProvider.DALLE3,
                style=style
            )

            return GeneratedImage(
                url=image_data.url,
                prompt=prompt,
                revised_prompt=image_data.revised_prompt,
                provider=ImageProvider.DALLE3,
                style=style,
                size=dalle_size,
                quality=quality,
                generation_time=generation_time,
                quality_score=quality_score,
                metadata={
                    "model": "dall-e-3",
                    "dalle_style": dalle_style,
                    "dalle_quality": dalle_quality
                }
            )

        except Exception as e:
            raise Exception(f"DALL-E 3 generation failed: {str(e)}")

    async def _generate_dalle2(
        self,
        prompt: str,
        size: ImageSize
    ) -> GeneratedImage:
        """Generate image using DALL-E 2 (cheaper, faster)"""

        start_time = datetime.now()

        # DALL-E 2 only supports specific sizes
        dalle2_size = "1024x1024"  # Default

        try:
            response = self.openai_client.images.generate(
                model="dall-e-2",
                prompt=prompt,
                size=dalle2_size,
                n=1
            )

            generation_time = (datetime.now() - start_time).total_seconds()

            image_data = response.data[0]

            quality_score = self._estimate_quality_score(
                prompt=prompt,
                provider=ImageProvider.DALLE2,
                style=ImageStyle.NATURAL
            )

            return GeneratedImage(
                url=image_data.url,
                prompt=prompt,
                provider=ImageProvider.DALLE2,
                style=ImageStyle.NATURAL,
                size=dalle2_size,
                quality=ImageQuality.STANDARD,
                generation_time=generation_time,
                quality_score=quality_score,
                metadata={"model": "dall-e-2"}
            )

        except Exception as e:
            raise Exception(f"DALL-E 2 generation failed: {str(e)}")

    def _map_to_dalle_size(self, size: ImageSize) -> str:
        """Map ImageSize to DALL-E supported sizes"""
        # DALL-E 3 supports: 1024x1024, 1792x1024, 1024x1792

        mapping = {
            ImageSize.SQUARE_1080: "1024x1024",
            ImageSize.LANDSCAPE_1200: "1792x1024",
            ImageSize.PORTRAIT_1080: "1024x1792",
            ImageSize.WIDE_1200: "1792x1024",
            ImageSize.DALLE_SQUARE: "1024x1024",
            ImageSize.DALLE_LANDSCAPE: "1792x1024",
            ImageSize.DALLE_PORTRAIT: "1024x1792"
        }

        return mapping.get(size, "1024x1024")

    def _estimate_quality_score(
        self,
        prompt: str,
        provider: ImageProvider,
        style: ImageStyle
    ) -> float:
        """
        Estimate quality score based on prompt and parameters
        Returns 0-100
        """

        score = 50.0  # Base score

        # Provider quality
        provider_scores = {
            ImageProvider.DALLE3: 20.0,
            ImageProvider.DALLE2: 10.0,
            ImageProvider.STABLE_DIFFUSION: 15.0
        }
        score += provider_scores.get(provider, 10.0)

        # Prompt detail and specificity
        prompt_length = len(prompt)
        if prompt_length > 200:
            score += 10.0
        elif prompt_length > 100:
            score += 5.0

        # Check for visual storytelling indicators
        storytelling_keywords = [
            'moment', 'scene', 'person', 'character', 'emotion',
            'action', 'narrative', 'story', 'expression', 'gesture'
        ]
        prompt_lower = prompt.lower()
        storytelling_score = sum(2 for kw in storytelling_keywords if kw in prompt_lower)
        score += min(storytelling_score, 10.0)

        # Technical quality indicators
        technical_keywords = [
            'lighting', 'composition', 'focus', 'depth of field',
            'cinematic', 'professional', 'award-winning', 'high quality'
        ]
        technical_score = sum(1.5 for kw in technical_keywords if kw in prompt_lower)
        score += min(technical_score, 10.0)

        return min(score, 100.0)

    async def generate_image_variants(
        self,
        base_prompt: str,
        num_variants: int = 3,
        style: ImageStyle = ImageStyle.NATURAL,
        size: ImageSize = ImageSize.DALLE_SQUARE
    ) -> List[GeneratedImage]:
        """
        Generate multiple image variants with different approaches

        Args:
            base_prompt: Base image description
            num_variants: Number of variants to create
            style: Base style (will be varied)
            size: Image size

        Returns:
            List of generated images
        """

        variants = []

        # Create prompt variations
        prompt_variations = self._create_prompt_variations(base_prompt, num_variants)

        for i, variant_prompt in enumerate(prompt_variations):
            # Vary style for diversity
            variant_style = self._get_variant_style(style, i)

            try:
                image = await self.generate_ad_image(
                    prompt=variant_prompt,
                    style=variant_style,
                    size=size,
                    quality=ImageQuality.HD
                )
                variants.append(image)
            except Exception as e:
                print(f"Failed to generate variant {i}: {e}")
                continue

        return variants

    def _create_prompt_variations(self, base_prompt: str, num: int) -> List[str]:
        """Create prompt variations for diverse outputs"""

        variations = []

        # Variation approaches
        approaches = [
            ("close-up shot", "intimate, detailed view"),
            ("wide angle shot", "environmental context, establishing shot"),
            ("hero shot", "bold, dramatic, center-focused"),
            ("lifestyle shot", "natural, candid, in-context"),
            ("conceptual shot", "creative, metaphorical, artistic interpretation")
        ]

        for i in range(min(num, len(approaches))):
            angle, description = approaches[i]
            variation = f"{base_prompt}, {angle}, {description}"
            variations.append(variation)

        return variations

    def _get_variant_style(self, base_style: ImageStyle, variant_index: int) -> ImageStyle:
        """Get style for variant to ensure diversity"""

        style_rotation = [
            ImageStyle.NATURAL,
            ImageStyle.VIVID,
            ImageStyle.CINEMATIC,
            ImageStyle.PHOTOGRAPHIC,
            ImageStyle.ARTISTIC
        ]

        # Start with base style, then rotate
        if variant_index == 0:
            return base_style

        return style_rotation[variant_index % len(style_rotation)]

    async def batch_generate_for_campaign(
        self,
        creative_prompts: List[str],
        platform: str,
        campaign_id: str
    ) -> Dict[str, List[GeneratedImage]]:
        """
        Generate images for entire campaign across multiple creatives

        Args:
            creative_prompts: List of image prompts from creatives
            platform: Target platform (Meta, Google, TikTok, etc.)
            campaign_id: Campaign identifier

        Returns:
            Dict mapping prompts to generated images
        """

        # Determine optimal sizes for platform
        platform_sizes = self._get_platform_sizes(platform)

        results = {}

        for prompt in creative_prompts:
            images = []
            for size in platform_sizes:
                try:
                    image = await self.generate_ad_image(
                        prompt=prompt,
                        size=size,
                        quality=ImageQuality.HD,
                        style=ImageStyle.VIVID if platform == "TikTok" else ImageStyle.NATURAL
                    )
                    images.append(image)
                except Exception as e:
                    print(f"Failed to generate {size} for prompt: {e}")
                    continue

            results[prompt] = images

        return results

    def _get_platform_sizes(self, platform: str) -> List[ImageSize]:
        """Get recommended image sizes for platform"""

        sizes = {
            "Meta": [
                ImageSize.SQUARE_1080,  # Feed
                ImageSize.PORTRAIT_1080,  # Story
                ImageSize.LANDSCAPE_1200  # Carousel
            ],
            "Instagram": [
                ImageSize.SQUARE_1080,
                ImageSize.PORTRAIT_1080
            ],
            "TikTok": [
                ImageSize.PORTRAIT_1080
            ],
            "LinkedIn": [
                ImageSize.LANDSCAPE_1200
            ],
            "Google": [
                ImageSize.LANDSCAPE_1200,
                ImageSize.SQUARE_1080
            ]
        }

        return sizes.get(platform, [ImageSize.SQUARE_1080])

    def validate_image_quality(
        self,
        image_url: str,
        minimum_score: float = 70.0
    ) -> Dict[str, Any]:
        """
        Validate generated image meets quality standards
        (Placeholder for future computer vision analysis)

        Args:
            image_url: URL of generated image
            minimum_score: Minimum acceptable quality score

        Returns:
            Validation result
        """

        # This would integrate with computer vision APIs to check:
        # - Image clarity and sharpness
        # - Composition quality
        # - Brand safety (no inappropriate content)
        # - Text readability if present
        # - Color quality

        # For now, return placeholder
        return {
            "valid": True,
            "score": 85.0,
            "passes_minimum": True,
            "checks": {
                "clarity": "pass",
                "composition": "pass",
                "brand_safe": "pass",
                "text_readable": "pass"
            }
        }
