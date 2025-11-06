"""
AI-Powered Creative Generation Service
Generates award-winning quality ad creatives using advanced AI models
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
import anthropic
import os
from enum import Enum


class CreativeTone(str, Enum):
    """Creative tone options"""
    INSPIRATIONAL = "inspirational"
    HUMOROUS = "humorous"
    EMOTIONAL = "emotional"
    PROFESSIONAL = "professional"
    BOLD = "bold"
    AUTHENTIC = "authentic"
    STORYTELLING = "storytelling"
    INNOVATIVE = "innovative"


class CreativeObjective(str, Enum):
    """Campaign objectives"""
    AWARENESS = "awareness"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    CONSIDERATION = "consideration"
    RETENTION = "retention"
    ADVOCACY = "advocacy"


class BrandVoice(BaseModel):
    """Brand voice definition"""
    personality_traits: List[str] = Field(
        description="3-5 brand personality traits (e.g., innovative, caring, bold)"
    )
    tone_preferences: List[CreativeTone] = Field(
        description="Preferred creative tones"
    )
    avoid_words: List[str] = Field(
        default=[],
        description="Words/phrases to avoid"
    )
    must_include: List[str] = Field(
        default=[],
        description="Required brand elements (taglines, key messages)"
    )
    target_audience: str = Field(
        description="Detailed target audience description"
    )
    brand_values: List[str] = Field(
        default=[],
        description="Core brand values (e.g., sustainability, innovation)"
    )


class CreativeBrief(BaseModel):
    """Comprehensive creative brief"""
    product_service: str = Field(description="Product or service being promoted")
    objective: CreativeObjective = Field(description="Primary campaign objective")
    key_message: str = Field(description="Core message to communicate")
    unique_value_prop: str = Field(description="What makes this offering unique")
    target_platform: str = Field(description="Meta, Google, TikTok, LinkedIn")
    brand_voice: BrandVoice
    campaign_theme: Optional[str] = Field(None, description="Overarching campaign theme")
    cultural_context: Optional[str] = Field(None, description="Cultural relevance/connection")
    social_impact: Optional[str] = Field(None, description="Social/environmental impact angle")
    competitors: Optional[List[str]] = Field(None, description="Key competitors")
    success_metrics: Optional[List[str]] = Field(None, description="How success will be measured")


class GeneratedCreative(BaseModel):
    """Generated creative output"""
    headline: str = Field(max_length=200)
    primary_text: str = Field(max_length=2000)
    description: str = Field(max_length=500)
    call_to_action: str
    image_prompt: str = Field(description="DALL-E/Midjourney prompt for image generation")
    video_concept: Optional[str] = Field(None, description="Video concept if applicable")
    quality_score: float = Field(description="Predicted quality score 0-100")
    quality_factors: Dict[str, float] = Field(description="Breakdown of quality factors")
    creative_rationale: str = Field(description="Why this creative should work")
    platform_optimizations: Dict[str, Any] = Field(description="Platform-specific tweaks")
    variant_type: str = Field(description="What makes this variant unique")


class CreativeGenerationService:
    """
    Advanced AI-powered creative generation service
    Produces award-winning quality ad creatives
    """

    def __init__(self):
        self.anthropic_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = "claude-sonnet-4-20250514"  # Latest Claude Sonnet

    # Award-winning campaign frameworks
    AWARD_WINNING_FRAMEWORKS = {
        "storytelling": {
            "structure": [
                "Hero's Journey",
                "Problem-Solution-Transformation",
                "Before-After-Bridge",
                "Brand Universe Building"
            ],
            "elements": [
                "Authentic human connection",
                "Emotional resonance",
                "Clear narrative arc",
                "Memorable characters or moments"
            ]
        },
        "innovation": {
            "approaches": [
                "Challenge conventions",
                "Reframe the category",
                "Create new experiences",
                "Push cultural conversations"
            ]
        },
        "craft": {
            "excellence_markers": [
                "Precise, powerful copywriting",
                "Visual-verbal harmony",
                "Attention to every detail",
                "Platform-native execution"
            ]
        },
        "impact": {
            "criteria": [
                "Clear, measurable objectives",
                "Meaningful engagement",
                "Social/cultural relevance",
                "Authentic purpose"
            ]
        }
    }

    async def generate_creative_concepts(
        self,
        brief: CreativeBrief,
        num_variants: int = 5,
        include_diverse_approaches: bool = True
    ) -> List[GeneratedCreative]:
        """
        Generate multiple high-quality creative concepts based on brief

        Args:
            brief: Comprehensive creative brief
            num_variants: Number of variants to generate
            include_diverse_approaches: Whether to use different creative strategies

        Returns:
            List of generated creative concepts with quality scoring
        """

        # Build comprehensive prompt for Claude
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_generation_prompt(brief, num_variants, include_diverse_approaches)

        # Call Claude API
        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=8000,
            temperature=0.8,  # Higher creativity
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )

        # Parse and structure response
        creatives = self._parse_creative_response(response.content[0].text, brief)

        # Score each creative
        for creative in creatives:
            creative.quality_score, creative.quality_factors = self._score_creative(
                creative, brief
            )

        # Sort by quality score
        creatives.sort(key=lambda x: x.quality_score, reverse=True)

        return creatives

    def _build_system_prompt(self) -> str:
        """Build system prompt for creative generation"""
        return """You are an award-winning creative director who has won multiple Webby Awards, Cannes Lions, and other prestigious advertising awards.

Your expertise includes:
- Crafting compelling narratives that resonate emotionally
- Creating authentic, purpose-driven campaigns
- Building complete brand universes, not just single ads
- Pushing creative boundaries while maintaining brand integrity
- Writing precise, powerful copy that drives action
- Understanding cultural context and social relevance
- Designing campaigns with measurable impact

Your creative philosophy:
1. AUTHENTICITY > Trendy gimmicks
2. STORYTELLING > Product features
3. EMOTIONAL CONNECTION > Rational arguments
4. CULTURAL RELEVANCE > Generic messaging
5. CRAFT EXCELLENCE > Good enough
6. MEANINGFUL IMPACT > Vanity metrics

When generating creatives:
- Start with the human insight, not the product
- Make every word count - no fluff
- Create visuals that tell stories, not just look pretty
- Ensure platform-native execution
- Build campaigns that could win awards
- Focus on what makes audiences feel, think, and act"""

    def _build_generation_prompt(
        self,
        brief: CreativeBrief,
        num_variants: int,
        include_diverse: bool
    ) -> str:
        """Build user prompt with creative brief"""

        diverse_note = ""
        if include_diverse:
            diverse_note = f"""
Generate {num_variants} DISTINCTLY DIFFERENT creative concepts using these varied approaches:
1. Emotional Storytelling (narrative-driven)
2. Bold & Provocative (challenge conventions)
3. Authentic Purpose (social impact focus)
4. Innovative Experience (new format/interaction)
5. Craft Excellence (stunning visual-verbal harmony)

Each variant should feel completely different in approach, tone, and execution.
"""
        else:
            diverse_note = f"Generate {num_variants} creative variants exploring different angles of the core message."

        brand_voice_section = f"""
BRAND VOICE:
- Personality: {', '.join(brief.brand_voice.personality_traits)}
- Tone: {', '.join([t.value for t in brief.brand_voice.tone_preferences])}
- Target Audience: {brief.brand_voice.target_audience}
- Brand Values: {', '.join(brief.brand_voice.brand_values)}
- Must Include: {', '.join(brief.brand_voice.must_include) if brief.brand_voice.must_include else 'None'}
- Avoid: {', '.join(brief.brand_voice.avoid_words) if brief.brand_voice.avoid_words else 'None'}
"""

        cultural_section = ""
        if brief.cultural_context or brief.social_impact:
            cultural_section = f"""
CULTURAL CONTEXT:
{brief.cultural_context or 'Not specified'}

SOCIAL IMPACT ANGLE:
{brief.social_impact or 'Not specified'}
"""

        return f"""Generate award-winning ad creatives for this campaign:

CREATIVE BRIEF:
==============
Product/Service: {brief.product_service}
Objective: {brief.objective.value}
Target Platform: {brief.target_platform}

Key Message: {brief.key_message}
Unique Value Prop: {brief.unique_value_prop}

Campaign Theme: {brief.campaign_theme or 'Not specified'}
{cultural_section}
{brand_voice_section}

{diverse_note}

For EACH creative variant, provide:

1. HEADLINE (max 100 chars)
   - Attention-grabbing, memorable
   - Can work as standalone message

2. PRIMARY TEXT (max 1500 chars)
   - Compelling narrative or argument
   - Authentic voice
   - Clear benefit/transformation
   - Emotionally resonant

3. DESCRIPTION (max 300 chars)
   - Reinforce key message
   - Add urgency or detail

4. CALL TO ACTION
   - Choose from: Shop Now, Learn More, Sign Up, Download, Watch Video, Get Started, Book Now, Apply Now

5. IMAGE CONCEPT & PROMPT
   - Describe the hero image/visual
   - Provide detailed DALL-E/Midjourney prompt
   - Ensure visual storytelling, not just product shots

6. VIDEO CONCEPT (if applicable)
   - 15-30 second video concept
   - Opening hook, narrative arc, closing

7. CREATIVE RATIONALE
   - Why this should work
   - What insight it's built on
   - Expected audience response

8. VARIANT TYPE
   - What makes this unique (e.g., "Emotional storytelling", "Bold provocation", etc.)

Format your response as JSON array with these fields for each creative:
{{
  "variants": [
    {{
      "headline": "...",
      "primary_text": "...",
      "description": "...",
      "call_to_action": "...",
      "image_prompt": "...",
      "video_concept": "...",
      "creative_rationale": "...",
      "variant_type": "...",
      "platform_optimizations": {{
        "{brief.target_platform}": {{
          "format_notes": "...",
          "targeting_suggestions": "...",
          "timing_notes": "..."
        }}
      }}
    }}
  ]
}}

Remember: Create campaigns that could win Webby Awards or Cannes Lions. Quality over everything."""

    def _parse_creative_response(
        self,
        response_text: str,
        brief: CreativeBrief
    ) -> List[GeneratedCreative]:
        """Parse Claude's response into structured creatives"""
        import json
        import re

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*"variants"[\s\S]*\}', response_text)
        if not json_match:
            raise ValueError("Could not parse creative response")

        data = json.loads(json_match.group())
        variants = data.get("variants", [])

        creatives = []
        for variant in variants:
            creative = GeneratedCreative(
                headline=variant.get("headline", "")[:200],
                primary_text=variant.get("primary_text", "")[:2000],
                description=variant.get("description", "")[:500],
                call_to_action=variant.get("call_to_action", "Learn More"),
                image_prompt=variant.get("image_prompt", ""),
                video_concept=variant.get("video_concept"),
                quality_score=0.0,  # Will be calculated
                quality_factors={},  # Will be calculated
                creative_rationale=variant.get("creative_rationale", ""),
                platform_optimizations=variant.get("platform_optimizations", {}),
                variant_type=variant.get("variant_type", "Standard")
            )
            creatives.append(creative)

        return creatives

    def _score_creative(
        self,
        creative: GeneratedCreative,
        brief: CreativeBrief
    ) -> tuple[float, Dict[str, float]]:
        """
        Score creative quality based on award-winning criteria
        Returns (total_score, factor_breakdown)
        """
        factors = {}

        # 1. Headline Impact (0-20 points)
        headline_score = self._score_headline(creative.headline)
        factors["headline_impact"] = headline_score

        # 2. Storytelling Quality (0-20 points)
        story_score = self._score_storytelling(creative.primary_text)
        factors["storytelling"] = story_score

        # 3. Authenticity & Brand Voice Alignment (0-15 points)
        voice_score = self._score_brand_voice(creative, brief.brand_voice)
        factors["brand_voice_alignment"] = voice_score

        # 4. Emotional Resonance (0-15 points)
        emotion_score = self._score_emotional_resonance(creative.primary_text)
        factors["emotional_resonance"] = emotion_score

        # 5. Visual Concept Quality (0-10 points)
        visual_score = self._score_visual_concept(creative.image_prompt)
        factors["visual_concept"] = visual_score

        # 6. Clarity & Persuasion (0-10 points)
        clarity_score = self._score_clarity(creative)
        factors["clarity_persuasion"] = clarity_score

        # 7. Innovation & Uniqueness (0-10 points)
        innovation_score = self._score_innovation(creative.variant_type, creative.creative_rationale)
        factors["innovation"] = innovation_score

        total_score = sum(factors.values())

        return total_score, factors

    def _score_headline(self, headline: str) -> float:
        """Score headline quality (0-20)"""
        score = 0.0

        # Length optimization (8-12 words ideal)
        word_count = len(headline.split())
        if 6 <= word_count <= 12:
            score += 5.0
        elif 5 <= word_count <= 15:
            score += 3.0

        # Presence of power words
        power_words = [
            'discover', 'unlock', 'transform', 'reveal', 'secret',
            'proven', 'guaranteed', 'free', 'new', 'exclusive',
            'limited', 'now', 'today', 'you', 'your'
        ]
        headline_lower = headline.lower()
        power_word_count = sum(1 for word in power_words if word in headline_lower)
        score += min(power_word_count * 2, 5.0)

        # Emotional trigger words
        emotion_words = [
            'love', 'fear', 'joy', 'hope', 'dream', 'inspire',
            'amaze', 'shock', 'surprise', 'believe', 'feel'
        ]
        emotion_count = sum(1 for word in emotion_words if word in headline_lower)
        score += min(emotion_count * 2, 5.0)

        # Question or statement variety
        if '?' in headline or '!' in headline:
            score += 2.0

        # Specificity (contains numbers or specific details)
        if any(char.isdigit() for char in headline):
            score += 3.0

        return min(score, 20.0)

    def _score_storytelling(self, text: str) -> float:
        """Score storytelling quality (0-20)"""
        score = 0.0

        # Length check (good stories need room)
        if len(text) >= 300:
            score += 5.0
        elif len(text) >= 150:
            score += 3.0

        # Narrative indicators
        narrative_markers = [
            'imagine', 'picture', 'story', 'journey', 'once',
            'when', 'then', 'finally', 'before', 'after',
            'transform', 'become', 'discover', 'realize'
        ]
        text_lower = text.lower()
        marker_count = sum(1 for marker in narrative_markers if marker in text_lower)
        score += min(marker_count * 1.5, 7.0)

        # Character/human element
        human_words = ['you', 'your', 'we', 'us', 'people', 'person', 'customer']
        human_count = sum(1 for word in human_words if word in text_lower)
        score += min(human_count * 0.5, 4.0)

        # Sensory language
        sensory_words = [
            'see', 'hear', 'feel', 'touch', 'taste', 'smell',
            'look', 'sound', 'bright', 'soft', 'warm', 'cold'
        ]
        sensory_count = sum(1 for word in sensory_words if word in text_lower)
        score += min(sensory_count * 1.0, 4.0)

        return min(score, 20.0)

    def _score_brand_voice(self, creative: GeneratedCreative, brand_voice: BrandVoice) -> float:
        """Score brand voice alignment (0-15)"""
        score = 0.0
        text = f"{creative.headline} {creative.primary_text}".lower()

        # Check for must-include elements
        if brand_voice.must_include:
            includes_count = sum(1 for item in brand_voice.must_include if item.lower() in text)
            score += (includes_count / len(brand_voice.must_include)) * 5.0
        else:
            score += 5.0  # Full points if no requirements

        # Check avoided words are not present
        if brand_voice.avoid_words:
            avoids_count = sum(1 for word in brand_voice.avoid_words if word.lower() in text)
            penalty = (avoids_count / len(brand_voice.avoid_words)) * 5.0
            score += max(0, 5.0 - penalty)
        else:
            score += 5.0

        # Tone alignment (simplified)
        score += 5.0  # Base score, would need more sophisticated NLP

        return min(score, 15.0)

    def _score_emotional_resonance(self, text: str) -> float:
        """Score emotional impact (0-15)"""
        score = 0.0
        text_lower = text.lower()

        # Emotional vocabulary
        emotion_categories = {
            'joy': ['happy', 'joy', 'delight', 'excited', 'thrilled', 'amazing', 'wonderful'],
            'trust': ['trust', 'believe', 'confident', 'reliable', 'secure', 'safe', 'proven'],
            'fear': ['worry', 'concern', 'risk', 'danger', 'protect', 'avoid', 'prevent'],
            'surprise': ['discover', 'reveal', 'unveil', 'surprise', 'unexpected', 'shocking'],
            'sadness': ['struggle', 'difficult', 'challenge', 'problem', 'pain', 'frustration'],
            'anticipation': ['imagine', 'future', 'coming', 'next', 'soon', 'tomorrow', 'ahead']
        }

        emotion_hits = 0
        for category, words in emotion_categories.items():
            if any(word in text_lower for word in words):
                emotion_hits += 1

        score += min(emotion_hits * 2.5, 10.0)

        # Benefit-oriented language
        benefit_words = ['get', 'gain', 'achieve', 'reach', 'attain', 'become', 'grow']
        benefit_count = sum(1 for word in benefit_words if word in text_lower)
        score += min(benefit_count * 1.0, 5.0)

        return min(score, 15.0)

    def _score_visual_concept(self, image_prompt: str) -> float:
        """Score visual concept quality (0-10)"""
        score = 0.0

        # Prompt detail and specificity
        if len(image_prompt) >= 100:
            score += 3.0
        elif len(image_prompt) >= 50:
            score += 2.0

        # Visual storytelling elements
        visual_elements = [
            'character', 'person', 'scene', 'setting', 'action',
            'emotion', 'expression', 'moment', 'narrative', 'story'
        ]
        prompt_lower = image_prompt.lower()
        element_count = sum(1 for elem in visual_elements if elem in prompt_lower)
        score += min(element_count * 1.5, 4.0)

        # Aesthetic descriptors
        aesthetic_words = [
            'beautiful', 'stunning', 'dramatic', 'cinematic', 'artistic',
            'color', 'lighting', 'composition', 'style', 'mood'
        ]
        aesthetic_count = sum(1 for word in aesthetic_words if word in prompt_lower)
        score += min(aesthetic_count * 1.0, 3.0)

        return min(score, 10.0)

    def _score_clarity(self, creative: GeneratedCreative) -> float:
        """Score message clarity and persuasion (0-10)"""
        score = 5.0  # Base score

        # Clear CTA present
        if creative.call_to_action:
            score += 2.0

        # Description reinforces headline
        if creative.description and len(creative.description) > 50:
            score += 3.0

        return min(score, 10.0)

    def _score_innovation(self, variant_type: str, rationale: str) -> float:
        """Score innovation and uniqueness (0-10)"""
        score = 0.0

        # Variant type suggests creative approach
        innovative_types = [
            'innovative', 'provocative', 'bold', 'experimental',
            'unconventional', 'disruptive', 'fresh', 'unique'
        ]
        variant_lower = variant_type.lower()
        if any(itype in variant_lower for itype in innovative_types):
            score += 4.0

        # Rationale shows strategic thinking
        if len(rationale) >= 100:
            score += 3.0

        # Insight-driven language in rationale
        insight_words = ['insight', 'because', 'understand', 'realize', 'believe', 'feel']
        rationale_lower = rationale.lower()
        insight_count = sum(1 for word in insight_words if word in rationale_lower)
        score += min(insight_count * 1.0, 3.0)

        return min(score, 10.0)

    async def generate_campaign_narrative(
        self,
        brief: CreativeBrief,
        creatives: List[GeneratedCreative]
    ) -> Dict[str, Any]:
        """
        Generate overarching campaign narrative and strategy
        For building complete brand universes, not just single ads
        """

        prompt = f"""You are a creative strategist developing an award-winning campaign.

Based on this brief and generated creatives, develop a comprehensive campaign narrative:

BRIEF:
{brief.model_dump_json(indent=2)}

TOP CREATIVES:
{[{"variant": c.variant_type, "headline": c.headline, "rationale": c.creative_rationale} for c in creatives[:3]]}

Provide:

1. CAMPAIGN BIG IDEA
   - The overarching concept that ties everything together
   - The human insight at the core

2. NARRATIVE ARC
   - How the campaign unfolds over time
   - Story progression across touchpoints

3. BRAND UNIVERSE ELEMENTS
   - How this creates an immersive brand experience
   - Extensions beyond individual ads (social, events, partnerships, etc.)

4. CULTURAL RELEVANCE
   - How this connects to current cultural moments
   - Why this matters now

5. EXPECTED IMPACT
   - Emotional response from audience
   - Behavioral outcomes
   - Business results

6. AWARD-WORTHINESS
   - Why this could win Webby Awards or Cannes Lions
   - Innovation and craft excellence elements

Format as JSON."""

        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=3000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        import json
        import re

        response_text = response.content[0].text
        json_match = re.search(r'\{[\s\S]*\}', response_text)

        if json_match:
            return json.loads(json_match.group())
        else:
            return {"narrative": response_text}

    async def optimize_for_platform(
        self,
        creative: GeneratedCreative,
        platform: str,
        format_type: str
    ) -> GeneratedCreative:
        """
        Optimize creative for specific platform and format

        Args:
            creative: Base creative
            platform: 'Meta', 'Google', 'TikTok', 'LinkedIn'
            format_type: 'feed', 'story', 'carousel', 'video', etc.

        Returns:
            Platform-optimized creative
        """

        # Platform-specific best practices
        platform_specs = {
            "Meta": {
                "feed": {
                    "headline_max": 40,
                    "text_max": 125,
                    "best_practices": [
                        "Front-load key message (first 90 chars)",
                        "Use emojis sparingly",
                        "Mobile-first thinking",
                        "Test without text overlay on images"
                    ]
                },
                "story": {
                    "text_max": 50,
                    "best_practices": [
                        "Vertical video 9:16",
                        "First 3 seconds are critical",
                        "Sound-off friendly",
                        "Interactive elements (polls, stickers)"
                    ]
                }
            },
            "TikTok": {
                "video": {
                    "duration": "15-30 seconds ideal",
                    "best_practices": [
                        "Hook in first 2 seconds",
                        "Native, authentic feel",
                        "Trending audio/effects",
                        "Fast-paced editing",
                        "Vertical 9:16 only"
                    ]
                }
            },
            "LinkedIn": {
                "feed": {
                    "headline_max": 150,
                    "text_max": 600,
                    "best_practices": [
                        "Professional but human tone",
                        "Data and insights",
                        "Thought leadership angle",
                        "Industry-specific language"
                    ]
                }
            },
            "Google": {
                "search": {
                    "headline_max": 30,
                    "description_max": 90,
                    "best_practices": [
                        "Include search intent keywords",
                        "Clear value prop in headline",
                        "Numbers and specifics",
                        "Match landing page message"
                    ]
                },
                "display": {
                    "best_practices": [
                        "Eye-catching visuals",
                        "Minimal text overlay",
                        "Strong brand presence",
                        "Clear CTA button"
                    ]
                }
            }
        }

        # Apply platform optimizations
        optimized = creative.model_copy()

        if platform in platform_specs and format_type in platform_specs[platform]:
            spec = platform_specs[platform][format_type]

            # Truncate if needed
            if "headline_max" in spec:
                optimized.headline = optimized.headline[:spec["headline_max"]]
            if "text_max" in spec:
                optimized.primary_text = optimized.primary_text[:spec["text_max"]]

            # Add platform notes
            optimized.platform_optimizations[platform] = {
                "format": format_type,
                "best_practices": spec.get("best_practices", []),
                "optimized": True
            }

        return optimized
