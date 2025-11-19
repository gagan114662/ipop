"""
AI Creative Generator Service - Generates award-winning creatives using AI.

This service uses OpenAI's DALL-E and GPT-4 Vision to generate
award-winning ad creatives by analyzing product images and
reference images from successful campaigns.
"""
import asyncio
import base64
import io
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import structlog
import httpx
from openai import AsyncOpenAI
from PIL import Image

from app.core.config import settings
from app.services.reference_image_finder import ReferenceImageFinder

logger = structlog.get_logger(__name__)


class AICreativeGenerator:
    """Generates award-winning creatives using AI."""

    def __init__(self, reference_finder: ReferenceImageFinder):
        """Initialize the AI creative generator."""
        self.reference_finder = reference_finder

        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")

        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.http_client = httpx.AsyncClient(timeout=60.0)

    async def generate_award_winning_creative(
        self,
        product_image_url: str,
        category: str,
        platform: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an award-winning creative using product and reference images.

        Args:
            product_image_url: URL to the product image
            category: Product category (e.g., "fashion", "tech", "food")
            platform: Target platform (e.g., "meta", "google", "tiktok")
            additional_context: Additional context like brand guidelines, copy, etc.

        Returns:
            Dict with generated creative details including image URL and metadata
        """
        try:
            logger.info(
                "creative_generation_started",
                category=category,
                platform=platform
            )

            # Step 1: Find reference images
            reference_images = await self.reference_finder.find_reference_images(
                category=category,
                count=3,
                platform=platform
            )

            if not reference_images:
                raise ValueError(f"No reference images found for category: {category}")

            # Step 2: Analyze product image and references using GPT-4 Vision
            analysis = await self._analyze_images(
                product_image_url,
                reference_images,
                category,
                platform,
                additional_context
            )

            # Step 3: Generate creative concept
            concept = await self._generate_creative_concept(
                analysis,
                category,
                platform,
                additional_context
            )

            # Step 4: Generate the actual creative image using DALL-E
            generated_image = await self._generate_creative_image(
                concept,
                analysis,
                platform
            )

            result = {
                "status": "success",
                "generated_image_url": generated_image["url"],
                "revised_prompt": generated_image.get("revised_prompt", ""),
                "concept": concept,
                "analysis": analysis,
                "reference_images": [
                    {
                        "url": ref["image_url"],
                        "title": ref.get("title", ""),
                        "source": ref.get("source", "")
                    }
                    for ref in reference_images
                ],
                "metadata": {
                    "category": category,
                    "platform": platform,
                    "generated_at": datetime.utcnow().isoformat(),
                    "model": settings.OPENAI_IMAGE_MODEL
                }
            }

            logger.info(
                "creative_generation_completed",
                category=category,
                platform=platform,
                success=True
            )

            return result

        except Exception as e:
            logger.error(
                "creative_generation_failed",
                category=category,
                platform=platform,
                error=str(e),
                exc_info=True
            )
            raise

    async def _analyze_images(
        self,
        product_image_url: str,
        reference_images: List[Dict[str, Any]],
        category: str,
        platform: str,
        additional_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze product and reference images using GPT-4 Vision.

        This identifies key visual elements, design patterns, and
        successful creative strategies from award-winning references.
        """
        try:
            # Prepare messages with images
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert creative director analyzing images for award-winning ad creative generation.
Your job is to analyze the product image and reference images to identify:
1. Key visual elements in the product
2. Successful design patterns from award-winning references
3. Color schemes and composition strategies
4. Typography and layout approaches
5. Emotional tone and messaging strategies
6. Platform-specific best practices

Provide detailed, actionable insights for creating an award-winning creative."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Analyze these images for creating an award-winning {category} ad creative for {platform}.

Product Image (below):"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": product_image_url}
                        },
                        {
                            "type": "text",
                            "text": f"\n\nReference Images (award-winning examples):"
                        }
                    ]
                }
            ]

            # Add reference images (limit to top 2 for API efficiency)
            for i, ref in enumerate(reference_images[:2], 1):
                messages[1]["content"].extend([
                    {
                        "type": "text",
                        "text": f"\n\nReference {i} - {ref.get('title', 'Award-winning creative')}:"
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": ref["image_url"]}
                    }
                ])

            # Add additional context if provided
            if additional_context:
                context_text = "\n\nAdditional Context:\n"
                if "brand_guidelines" in additional_context:
                    context_text += f"Brand Guidelines: {additional_context['brand_guidelines']}\n"
                if "target_audience" in additional_context:
                    context_text += f"Target Audience: {additional_context['target_audience']}\n"
                if "key_message" in additional_context:
                    context_text += f"Key Message: {additional_context['key_message']}\n"

                messages[1]["content"].append({
                    "type": "text",
                    "text": context_text
                })

            messages[1]["content"].append({
                "type": "text",
                "text": """\n\nProvide a detailed analysis covering:
1. Product visual elements and unique features
2. Key design patterns from references that we should adopt
3. Recommended color scheme and composition
4. Typography and layout strategy
5. Emotional tone and messaging approach
6. Platform-specific optimizations for best performance"""
            })

            # Call GPT-4 Vision
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=1500,
                temperature=0.7
            )

            analysis_text = response.choices[0].message.content

            logger.info(
                "image_analysis_completed",
                category=category,
                platform=platform,
                tokens_used=response.usage.total_tokens
            )

            return {
                "analysis_text": analysis_text,
                "tokens_used": response.usage.total_tokens,
                "model": settings.OPENAI_MODEL
            }

        except Exception as e:
            logger.error(
                "image_analysis_failed",
                error=str(e),
                exc_info=True
            )
            raise

    async def _generate_creative_concept(
        self,
        analysis: Dict[str, Any],
        category: str,
        platform: str,
        additional_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a creative concept based on the image analysis.

        This creates a detailed creative brief including visual style,
        composition, messaging, and platform-specific elements.
        """
        try:
            context_text = ""
            if additional_context:
                if "brand_name" in additional_context:
                    context_text += f"\nBrand: {additional_context['brand_name']}"
                if "key_message" in additional_context:
                    context_text += f"\nKey Message: {additional_context['key_message']}"
                if "cta" in additional_context:
                    context_text += f"\nCall-to-Action: {additional_context['cta']}"

            messages = [
                {
                    "role": "system",
                    "content": """You are a creative strategist for award-winning ad campaigns.
Based on image analysis, create a detailed creative concept that will generate high-performing ad creatives.
Focus on clarity, impact, and platform-specific best practices."""
                },
                {
                    "role": "user",
                    "content": f"""Based on this image analysis, create a detailed creative concept for a {category} ad on {platform}.

Image Analysis:
{analysis['analysis_text']}
{context_text}

Provide a creative concept with:
1. Visual Style (specific design direction)
2. Composition (layout and hierarchy)
3. Color Strategy (specific colors and mood)
4. Typography (font style and text placement)
5. Key Visual Elements (what to include/highlight)
6. Emotional Tone (feeling to convey)
7. Platform Optimizations (specific to {platform})
8. Detailed Image Generation Prompt (for DALL-E 3)

The image generation prompt should be highly detailed and specific, describing exactly what the creative should look like."""
                }
            ]

            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                max_tokens=2000,
                temperature=0.8
            )

            concept_text = response.choices[0].message.content

            logger.info(
                "creative_concept_generated",
                category=category,
                platform=platform,
                tokens_used=response.usage.total_tokens
            )

            return {
                "concept_text": concept_text,
                "tokens_used": response.usage.total_tokens,
                "model": "gpt-4-turbo-preview"
            }

        except Exception as e:
            logger.error(
                "concept_generation_failed",
                error=str(e),
                exc_info=True
            )
            raise

    async def _generate_creative_image(
        self,
        concept: Dict[str, Any],
        analysis: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """
        Generate the actual creative image using DALL-E 3.

        Uses the creative concept to generate a high-quality image
        optimized for the target platform.
        """
        try:
            # Extract the image generation prompt from concept
            concept_text = concept["concept_text"]

            # Build platform-specific sizing and requirements
            platform_specs = self._get_platform_specifications(platform)

            # Create DALL-E prompt
            dalle_prompt = f"""Create a professional, award-winning ad creative with these specifications:

{concept_text}

Technical Requirements:
- High-quality, professional advertising photography/design
- {platform_specs['description']}
- Optimized for {platform} advertising platform
- Eye-catching and engaging
- Clear visual hierarchy
- Brand-safe and appropriate for advertising

Style: Award-winning commercial photography, professional ad design, high-end production quality"""

            logger.info(
                "generating_image_with_dalle",
                platform=platform,
                prompt_length=len(dalle_prompt)
            )

            # Generate image with DALL-E 3
            response = await self.openai_client.images.generate(
                model=settings.OPENAI_IMAGE_MODEL,
                prompt=dalle_prompt[:4000],  # DALL-E 3 prompt limit
                size=platform_specs["size"],
                quality="hd",
                n=1
            )

            generated_image = {
                "url": response.data[0].url,
                "revised_prompt": response.data[0].revised_prompt,
                "size": platform_specs["size"],
                "model": settings.OPENAI_IMAGE_MODEL
            }

            logger.info(
                "image_generated_successfully",
                platform=platform,
                image_url=generated_image["url"]
            )

            return generated_image

        except Exception as e:
            logger.error(
                "image_generation_failed",
                error=str(e),
                exc_info=True
            )
            raise

    def _get_platform_specifications(self, platform: str) -> Dict[str, str]:
        """Get image size and specifications for each platform."""
        specs = {
            "meta": {
                "size": "1024x1024",
                "description": "Square format suitable for Facebook/Instagram feed and stories"
            },
            "facebook": {
                "size": "1024x1024",
                "description": "Square format optimized for Facebook feed"
            },
            "instagram": {
                "size": "1024x1024",
                "description": "Square format optimized for Instagram feed"
            },
            "google": {
                "size": "1024x1024",
                "description": "Square responsive display ad format"
            },
            "tiktok": {
                "size": "1024x1024",
                "description": "Vertical video-style format for TikTok"
            },
            "linkedin": {
                "size": "1024x1024",
                "description": "Professional square format for LinkedIn feed"
            }
        }

        return specs.get(
            platform.lower(),
            {
                "size": "1024x1024",
                "description": "Universal square format"
            }
        )

    async def generate_multiple_variants(
        self,
        product_image_url: str,
        category: str,
        platform: str,
        count: int = 3,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple creative variants for A/B testing.

        Args:
            product_image_url: URL to the product image
            category: Product category
            platform: Target platform
            count: Number of variants to generate
            additional_context: Additional context

        Returns:
            List of generated creative variants
        """
        try:
            logger.info(
                "generating_multiple_variants",
                count=count,
                category=category,
                platform=platform
            )

            # Generate variants concurrently
            tasks = [
                self.generate_award_winning_creative(
                    product_image_url,
                    category,
                    platform,
                    additional_context
                )
                for _ in range(count)
            ]

            variants = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out any exceptions
            successful_variants = [
                v for v in variants
                if not isinstance(v, Exception)
            ]

            logger.info(
                "variants_generated",
                requested=count,
                successful=len(successful_variants)
            )

            return successful_variants

        except Exception as e:
            logger.error(
                "variant_generation_failed",
                error=str(e),
                exc_info=True
            )
            raise

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()


async def get_ai_generator(reference_finder: ReferenceImageFinder) -> AICreativeGenerator:
    """Get AI creative generator instance."""
    return AICreativeGenerator(reference_finder)
