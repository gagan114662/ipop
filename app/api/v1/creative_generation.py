"""
API endpoints for AI-powered creative generation
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.creative_generation import (
    CreativeGenerationService,
    CreativeBrief,
    BrandVoice,
    CreativeTone,
    CreativeObjective,
    GeneratedCreative
)
from app.services.image_generation import (
    ImageGenerationService,
    ImageStyle,
    ImageSize,
    ImageQuality,
    GeneratedImage
)
from app.models.creative import Creative, CreativeType, CallToAction
from app.core.auth import get_current_client
from app.core.database import get_database
from pydantic import BaseModel, Field


router = APIRouter(prefix="/creative-generation", tags=["Creative Generation"])


# ==================== REQUEST MODELS ====================

class GenerateCreativesRequest(BaseModel):
    """Request to generate new creatives"""
    brief: CreativeBrief
    num_variants: int = Field(default=5, ge=1, le=10)
    include_diverse_approaches: bool = Field(default=True)
    generate_images: bool = Field(default=False)
    save_to_campaign: Optional[str] = Field(None, description="Campaign ID to save creatives to")


class GenerateImagesRequest(BaseModel):
    """Request to generate images for creatives"""
    prompts: List[str] = Field(description="Image prompts")
    style: ImageStyle = ImageStyle.NATURAL
    size: ImageSize = ImageSize.DALLE_SQUARE
    quality: ImageQuality = ImageQuality.HD
    platform: Optional[str] = Field(None, description="Target platform for size optimization")


class OptimizeCreativeRequest(BaseModel):
    """Request to optimize creative for platform"""
    creative_id: str
    platform: str = Field(description="Meta, Google, TikTok, LinkedIn")
    format_type: str = Field(description="feed, story, carousel, video, etc.")


class GenerateCampaignRequest(BaseModel):
    """Request to generate full campaign"""
    brief: CreativeBrief
    campaign_name: str
    num_creative_variants: int = Field(default=5, ge=3, le=10)
    generate_images: bool = Field(default=True)
    platforms: List[str] = Field(description="Target platforms")


# ==================== RESPONSE MODELS ====================

class GeneratedCreativeResponse(BaseModel):
    """Response with generated creatives"""
    creatives: List[GeneratedCreative]
    campaign_narrative: Optional[Dict[str, Any]] = None
    generation_time: float
    total_quality_score: float
    recommendations: List[str]


class GeneratedImagesResponse(BaseModel):
    """Response with generated images"""
    images: List[GeneratedImage]
    generation_time: float
    average_quality_score: float


class CampaignGenerationResponse(BaseModel):
    """Response for full campaign generation"""
    campaign_id: str
    campaign_name: str
    creative_ids: List[str]
    creatives: List[GeneratedCreative]
    images: Dict[str, List[GeneratedImage]]
    campaign_narrative: Dict[str, Any]
    total_generation_time: float
    overall_quality_score: float


# ==================== API ENDPOINTS ====================

@router.post("/generate", response_model=GeneratedCreativeResponse)
async def generate_creatives(
    request: GenerateCreativesRequest,
    client_id: str = Depends(get_current_client),
    db = Depends(get_database)
):
    """
    Generate award-winning quality ad creatives based on creative brief

    This endpoint uses advanced AI to generate multiple creative variants
    following award-winning campaign principles from Webby Awards, Cannes Lions, etc.
    """

    start_time = datetime.now()

    try:
        # Initialize services
        creative_service = CreativeGenerationService()

        # Generate creatives
        creatives = await creative_service.generate_creative_concepts(
            brief=request.brief,
            num_variants=request.num_variants,
            include_diverse_approaches=request.include_diverse_approaches
        )

        # Generate campaign narrative
        campaign_narrative = await creative_service.generate_campaign_narrative(
            brief=request.brief,
            creatives=creatives
        )

        # Generate images if requested
        if request.generate_images:
            image_service = ImageGenerationService()
            for creative in creatives:
                try:
                    image = await image_service.generate_ad_image(
                        prompt=creative.image_prompt,
                        style=ImageStyle.VIVID,
                        quality=ImageQuality.HD
                    )
                    # Store image URL in metadata
                    creative.platform_optimizations["generated_image"] = {
                        "url": image.url,
                        "quality_score": image.quality_score
                    }
                except Exception as e:
                    print(f"Image generation failed for creative: {e}")

        # Save to campaign if specified
        if request.save_to_campaign:
            saved_ids = []
            for creative in creatives:
                # Convert to Creative model
                db_creative = Creative(
                    client_id=client_id,
                    name=f"{creative.variant_type} - {creative.headline[:30]}",
                    type=CreativeType.IMAGE,  # Default, adjust based on needs
                    headline=creative.headline,
                    primary_text=creative.primary_text,
                    description=creative.description,
                    call_to_action=CallToAction(creative.call_to_action),
                    media_url=creative.platform_optimizations.get("generated_image", {}).get("url"),
                    performance_score=creative.quality_score,
                    metadata={
                        "generated": True,
                        "brief": request.brief.model_dump(),
                        "quality_factors": creative.quality_factors,
                        "rationale": creative.creative_rationale,
                        "image_prompt": creative.image_prompt
                    }
                )

                # Insert into database
                result = await db.creatives.insert_one(db_creative.model_dump())
                saved_ids.append(str(result.inserted_id))

            print(f"Saved {len(saved_ids)} creatives to campaign {request.save_to_campaign}")

        generation_time = (datetime.now() - start_time).total_seconds()

        # Calculate average quality
        avg_quality = sum(c.quality_score for c in creatives) / len(creatives) if creatives else 0

        # Generate recommendations
        recommendations = _generate_recommendations(creatives, request.brief)

        return GeneratedCreativeResponse(
            creatives=creatives,
            campaign_narrative=campaign_narrative,
            generation_time=generation_time,
            total_quality_score=avg_quality,
            recommendations=recommendations
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Creative generation failed: {str(e)}")


@router.post("/generate-images", response_model=GeneratedImagesResponse)
async def generate_images(
    request: GenerateImagesRequest,
    client_id: str = Depends(get_current_client)
):
    """
    Generate high-quality images for ad creatives

    Uses DALL-E 3 and other AI image generation services to create
    professional, award-winning quality visuals.
    """

    start_time = datetime.now()

    try:
        image_service = ImageGenerationService()

        images = []

        # Generate for each prompt
        for prompt in request.prompts:
            if request.platform:
                # Generate multiple sizes for platform
                platform_images = await image_service.batch_generate_for_campaign(
                    creative_prompts=[prompt],
                    platform=request.platform,
                    campaign_id="temp"
                )
                images.extend(platform_images.get(prompt, []))
            else:
                # Single image
                image = await image_service.generate_ad_image(
                    prompt=prompt,
                    style=request.style,
                    size=request.size,
                    quality=request.quality
                )
                images.append(image)

        generation_time = (datetime.now() - start_time).total_seconds()
        avg_quality = sum(img.quality_score for img in images) / len(images) if images else 0

        return GeneratedImagesResponse(
            images=images,
            generation_time=generation_time,
            average_quality_score=avg_quality
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@router.post("/optimize-for-platform")
async def optimize_creative_for_platform(
    request: OptimizeCreativeRequest,
    client_id: str = Depends(get_current_client),
    db = Depends(get_database)
):
    """
    Optimize an existing creative for specific platform and format

    Takes a generated creative and adapts it to platform-specific
    best practices and format requirements.
    """

    try:
        # Fetch creative from database
        creative_doc = await db.creatives.find_one({
            "_id": request.creative_id,
            "client_id": client_id
        })

        if not creative_doc:
            raise HTTPException(status_code=404, detail="Creative not found")

        # Convert to GeneratedCreative if it was AI-generated
        if creative_doc.get("metadata", {}).get("generated"):
            generated_creative = GeneratedCreative(
                headline=creative_doc["headline"],
                primary_text=creative_doc["primary_text"],
                description=creative_doc["description"],
                call_to_action=creative_doc["call_to_action"],
                image_prompt=creative_doc["metadata"].get("image_prompt", ""),
                quality_score=creative_doc.get("performance_score", 0),
                quality_factors=creative_doc["metadata"].get("quality_factors", {}),
                creative_rationale=creative_doc["metadata"].get("rationale", ""),
                platform_optimizations=creative_doc.get("metadata", {}).get("platform_optimizations", {}),
                variant_type=creative_doc.get("metadata", {}).get("variant_type", "Standard")
            )

            # Optimize
            creative_service = CreativeGenerationService()
            optimized = await creative_service.optimize_for_platform(
                creative=generated_creative,
                platform=request.platform,
                format_type=request.format_type
            )

            return {
                "original": generated_creative.model_dump(),
                "optimized": optimized.model_dump(),
                "changes": {
                    "headline_changed": generated_creative.headline != optimized.headline,
                    "text_changed": generated_creative.primary_text != optimized.primary_text,
                    "platform_notes": optimized.platform_optimizations.get(request.platform, {})
                }
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Creative was not AI-generated, cannot optimize"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.post("/generate-campaign", response_model=CampaignGenerationResponse)
async def generate_full_campaign(
    request: GenerateCampaignRequest,
    background_tasks: BackgroundTasks,
    client_id: str = Depends(get_current_client),
    db = Depends(get_database)
):
    """
    Generate a complete award-winning campaign

    Creates multiple creative variants, generates images, builds campaign narrative,
    and optimizes for multiple platforms - all in one request.

    This is the most comprehensive endpoint for creating campaigns that could
    win Webby Awards or Cannes Lions.
    """

    start_time = datetime.now()

    try:
        creative_service = CreativeGenerationService()
        image_service = ImageGenerationService()

        # 1. Generate creatives
        creatives = await creative_service.generate_creative_concepts(
            brief=request.brief,
            num_variants=request.num_creative_variants,
            include_diverse_approaches=True
        )

        # 2. Generate campaign narrative
        campaign_narrative = await creative_service.generate_campaign_narrative(
            brief=request.brief,
            creatives=creatives
        )

        # 3. Generate images if requested
        images_by_creative = {}
        if request.generate_images:
            for i, creative in enumerate(creatives):
                creative_images = []

                # Generate for each platform
                for platform in request.platforms:
                    platform_sizes = image_service._get_platform_sizes(platform)

                    for size in platform_sizes[:1]:  # One size per platform for now
                        try:
                            image = await image_service.generate_ad_image(
                                prompt=creative.image_prompt,
                                size=size,
                                style=ImageStyle.VIVID if platform == "TikTok" else ImageStyle.NATURAL,
                                quality=ImageQuality.HD
                            )
                            creative_images.append(image)
                        except Exception as e:
                            print(f"Image generation failed: {e}")

                images_by_creative[f"creative_{i}"] = creative_images

        # 4. Create campaign in database
        campaign_doc = {
            "client_id": client_id,
            "name": request.campaign_name,
            "brief": request.brief.model_dump(),
            "narrative": campaign_narrative,
            "status": "draft",
            "platforms": request.platforms,
            "created_at": datetime.utcnow(),
            "ai_generated": True
        }

        campaign_result = await db.campaigns.insert_one(campaign_doc)
        campaign_id = str(campaign_result.inserted_id)

        # 5. Save creatives to database
        creative_ids = []
        for i, creative in enumerate(creatives):
            # Get primary image URL
            creative_images = images_by_creative.get(f"creative_{i}", [])
            primary_image_url = creative_images[0].url if creative_images else None

            db_creative = {
                "client_id": client_id,
                "campaign_id": campaign_id,
                "name": f"{creative.variant_type} - {creative.headline[:30]}",
                "type": "IMAGE",
                "headline": creative.headline,
                "primary_text": creative.primary_text,
                "description": creative.description,
                "call_to_action": creative.call_to_action,
                "media_url": primary_image_url,
                "performance_score": creative.quality_score,
                "status": "DRAFT",
                "metadata": {
                    "generated": True,
                    "variant_type": creative.variant_type,
                    "quality_factors": creative.quality_factors,
                    "rationale": creative.creative_rationale,
                    "image_prompt": creative.image_prompt,
                    "platform_optimizations": creative.platform_optimizations,
                    "generated_images": [
                        {
                            "url": img.url,
                            "size": img.size,
                            "quality_score": img.quality_score
                        }
                        for img in creative_images
                    ]
                },
                "created_at": datetime.utcnow()
            }

            result = await db.creatives.insert_one(db_creative)
            creative_ids.append(str(result.inserted_id))

        generation_time = (datetime.now() - start_time).total_seconds()
        avg_quality = sum(c.quality_score for c in creatives) / len(creatives) if creatives else 0

        return CampaignGenerationResponse(
            campaign_id=campaign_id,
            campaign_name=request.campaign_name,
            creative_ids=creative_ids,
            creatives=creatives,
            images=images_by_creative,
            campaign_narrative=campaign_narrative,
            total_generation_time=generation_time,
            overall_quality_score=avg_quality
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign generation failed: {str(e)}")


@router.get("/quality-guidelines")
async def get_quality_guidelines():
    """
    Get award-winning creative quality guidelines

    Returns best practices, frameworks, and scoring criteria
    used to generate high-quality creatives.
    """

    return {
        "frameworks": CreativeGenerationService.AWARD_WINNING_FRAMEWORKS,
        "scoring_criteria": {
            "headline_impact": {
                "weight": 20,
                "factors": [
                    "Optimal length (6-12 words)",
                    "Power words and emotional triggers",
                    "Specificity and numbers",
                    "Question or exclamation"
                ]
            },
            "storytelling": {
                "weight": 20,
                "factors": [
                    "Narrative structure",
                    "Human element",
                    "Sensory language",
                    "Transformation arc"
                ]
            },
            "brand_voice_alignment": {
                "weight": 15,
                "factors": [
                    "Must-include elements present",
                    "Avoided words not used",
                    "Tone consistency"
                ]
            },
            "emotional_resonance": {
                "weight": 15,
                "factors": [
                    "Emotional vocabulary",
                    "Benefit-oriented language",
                    "Authentic connection"
                ]
            },
            "visual_concept": {
                "weight": 10,
                "factors": [
                    "Visual storytelling",
                    "Aesthetic quality",
                    "Production value"
                ]
            },
            "clarity_persuasion": {
                "weight": 10,
                "factors": [
                    "Clear message",
                    "Strong CTA",
                    "Value proposition"
                ]
            },
            "innovation": {
                "weight": 10,
                "factors": [
                    "Unique approach",
                    "Strategic insight",
                    "Creative boldness"
                ]
            }
        },
        "platform_best_practices": {
            "Meta": [
                "Front-load key message in first 90 characters",
                "Mobile-first design",
                "Test without text overlay on images",
                "Use authentic, relatable visuals"
            ],
            "TikTok": [
                "Hook in first 2 seconds",
                "Native, authentic feel",
                "Vertical 9:16 format only",
                "Fast-paced editing"
            ],
            "LinkedIn": [
                "Professional but human tone",
                "Data and insights",
                "Thought leadership angle",
                "Industry-specific language"
            ],
            "Google": [
                "Include search intent keywords",
                "Clear value prop in headline",
                "Numbers and specifics",
                "Match landing page message"
            ]
        },
        "award_winning_principles": [
            "Start with human insight, not product features",
            "Build authentic, purpose-driven narratives",
            "Create complete brand universes, not just ads",
            "Push creative boundaries while maintaining integrity",
            "Ensure cultural relevance and social impact",
            "Craft with excellence in every detail",
            "Design for measurable, meaningful outcomes"
        ]
    }


# ==================== HELPER FUNCTIONS ====================

def _generate_recommendations(
    creatives: List[GeneratedCreative],
    brief: CreativeBrief
) -> List[str]:
    """Generate recommendations based on generated creatives"""

    recommendations = []

    # Quality recommendations
    avg_quality = sum(c.quality_score for c in creatives) / len(creatives) if creatives else 0

    if avg_quality >= 80:
        recommendations.append("✅ Excellent quality - These creatives are ready for testing")
    elif avg_quality >= 70:
        recommendations.append("⚠️ Good quality - Consider A/B testing variants to identify winners")
    else:
        recommendations.append("⚠️ Quality could be improved - Review brief and regenerate")

    # Diversity check
    variant_types = set(c.variant_type for c in creatives)
    if len(variant_types) >= 4:
        recommendations.append("✅ Good creative diversity - Multiple approaches covered")
    else:
        recommendations.append("💡 Consider generating more diverse variants")

    # Platform recommendations
    if brief.target_platform == "TikTok":
        recommendations.append("📱 TikTok: Ensure video concepts are native and authentic")
        recommendations.append("📱 TikTok: Test with trending audio and effects")
    elif brief.target_platform == "LinkedIn":
        recommendations.append("💼 LinkedIn: Add data points and industry insights for credibility")

    # Testing recommendations
    recommendations.append("🧪 Run A/B tests with top 3 variants")
    recommendations.append("📊 Set clear success metrics before launching")

    # Image recommendations
    if any(c.image_prompt for c in creatives):
        recommendations.append("🎨 Generate images for top 3 variants first")
        recommendations.append("🎨 Test multiple visual styles to find what resonates")

    return recommendations
