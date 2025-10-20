"""Layer 4: Competitive Semiotics

This layer analyzes competitive positioning through visual and verbal codes:
- Visual code extraction (colors, layouts, styles, aesthetics)
- Verbal code extraction (messaging themes, tone, language patterns)
- Semiotic mapping (plotting competitive territory)
- White space identification (unclaimed positioning opportunities)

Mock implementation for now - will integrate GPT-4 Vision API later.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.strategy_engine.analysis.models import VisualCode

logger = logging.getLogger(__name__)


class CompetitiveSemiotics:
    """Analyzes competitive positioning through semiotic lens."""

    def __init__(self):
        """Initialize the competitive semiotics analyzer."""
        self.logger = logger

    async def extract_visual_codes(
        self,
        images: List[str],
        brand_name: str,
        use_mock: bool = False
    ) -> List[VisualCode]:
        """
        Extract visual codes from competitor images.

        Args:
            images: List of image file paths
            brand_name: Brand name for context
            use_mock: If True, use mock data instead of actual analysis

        Returns:
            List of VisualCode objects with dominant visual patterns
        """
        self.logger.info(f"Extracting visual codes from {len(images)} images for {brand_name}")

        # Mock implementation - returns simulated visual codes
        # TODO: Integrate GPT-4 Vision API for real analysis

        if use_mock or len(images) == 0:
            return self._mock_visual_codes()

        # Check if images exist
        existing_images = [img for img in images if Path(img).exists()]

        if len(existing_images) == 0:
            self.logger.warning("No valid image paths found, using mock data")
            return self._mock_visual_codes()

        # For now, return mock codes based on image count
        # Real implementation will use vision models
        mock_codes = self._mock_visual_codes()

        # Adjust frequency based on actual image count
        for code in mock_codes:
            code.examples = existing_images[:min(len(existing_images), 3)]

        return mock_codes

    def _mock_visual_codes(self) -> List[VisualCode]:
        """Generate mock visual codes for testing."""
        return [
            VisualCode(
                code_name="minimalist_aesthetic",
                frequency=0.75,
                examples=["image1.jpg", "image2.jpg", "image3.jpg"]
            ),
            VisualCode(
                code_name="warm_color_palette",
                frequency=0.60,
                examples=["image1.jpg", "image4.jpg"]
            ),
            VisualCode(
                code_name="product_hero_shot",
                frequency=0.80,
                examples=["image2.jpg", "image3.jpg", "image5.jpg"]
            ),
            VisualCode(
                code_name="natural_lighting",
                frequency=0.65,
                examples=["image1.jpg", "image3.jpg"]
            ),
            VisualCode(
                code_name="geometric_composition",
                frequency=0.45,
                examples=["image4.jpg"]
            )
        ]

    async def extract_verbal_codes(
        self,
        copy: List[str],
        brand_name: str
    ) -> Dict[str, Any]:
        """
        Extract verbal/messaging codes from brand copy.

        Args:
            copy: List of brand copy/messaging samples
            brand_name: Brand name for context

        Returns:
            Dictionary with dominant themes, tone, and messaging patterns
        """
        self.logger.info(f"Extracting verbal codes from {len(copy)} copy samples for {brand_name}")

        # Simple keyword-based analysis (mock)
        # TODO: Use LLM for deeper linguistic analysis

        # Extract themes from keywords
        themes = self._extract_themes_from_copy(copy)

        # Analyze tone
        tone = self._analyze_tone(copy)

        # Identify messaging patterns
        patterns = self._identify_messaging_patterns(copy)

        return {
            "dominant_themes": themes,
            "tone": tone,
            "messaging_patterns": patterns
        }

    def _extract_themes_from_copy(self, copy: List[str]) -> List[str]:
        """Extract dominant themes from copy."""
        theme_keywords = {
            "premium": ["premium", "luxury", "exclusive", "elite", "high-end"],
            "quality": ["quality", "craftsmanship", "artisan", "handcrafted", "authentic"],
            "sustainability": ["sustainable", "ethical", "eco", "green", "conscious"],
            "innovation": ["innovative", "modern", "cutting-edge", "advanced", "next-gen"],
            "accessibility": ["accessible", "affordable", "everyday", "simple", "easy"],
            "heritage": ["heritage", "traditional", "timeless", "classic", "legacy"]
        }

        themes = []
        copy_text = " ".join(copy).lower()

        for theme, keywords in theme_keywords.items():
            if any(keyword in copy_text for keyword in keywords):
                themes.append(theme)

        return themes if themes else ["quality", "premium"]

    def _analyze_tone(self, copy: List[str]) -> str:
        """Analyze overall tone of messaging."""
        copy_text = " ".join(copy).lower()

        if any(word in copy_text for word in ["exclusive", "luxury", "elite", "sophisticated"]):
            return "aspirational"
        elif any(word in copy_text for word in ["fun", "playful", "vibrant", "colorful"]):
            return "playful"
        elif any(word in copy_text for word in ["sustainable", "ethical", "conscious", "responsible"]):
            return "conscious"
        elif any(word in copy_text for word in ["innovative", "cutting-edge", "revolutionary"]):
            return "innovative"
        else:
            return "professional"

    def _identify_messaging_patterns(self, copy: List[str]) -> List[str]:
        """Identify messaging patterns."""
        patterns = []

        copy_text = " ".join(copy).lower()

        if "you" in copy_text or "your" in copy_text:
            patterns.append("direct_address")

        if any(word in copy_text for word in ["discover", "explore", "experience"]):
            patterns.append("invitation_to_explore")

        if any(word in copy_text for word in ["because", "that's why", "so you can"]):
            patterns.append("benefit_driven")

        if any(word in copy_text for word in ["introducing", "new", "now"]):
            patterns.append("news_announcement")

        return patterns if patterns else ["descriptive"]

    async def build_semiotic_map(
        self,
        competitors_data: Dict[str, Dict[str, List[str]]]
    ) -> Dict[str, Any]:
        """
        Build competitive semiotic map.

        Args:
            competitors_data: Dict mapping competitor names to their visual/verbal codes

        Returns:
            Semiotic map showing competitive territories
        """
        self.logger.info(f"Building semiotic map for {len(competitors_data)} competitors")

        # Aggregate all visual codes
        all_visual_codes = []
        for competitor, data in competitors_data.items():
            all_visual_codes.extend(data.get("visual_codes", []))

        # Aggregate all verbal codes
        all_verbal_codes = []
        for competitor, data in competitors_data.items():
            all_verbal_codes.extend(data.get("verbal_codes", []))

        # Map competitor positions
        competitor_positions = {}
        for competitor, data in competitors_data.items():
            competitor_positions[competitor] = {
                "visual_codes": data.get("visual_codes", []),
                "verbal_codes": data.get("verbal_codes", []),
                "positioning_cluster": self._determine_cluster(data)
            }

        return {
            "visual_territory": self._map_visual_territory(all_visual_codes),
            "verbal_territory": self._map_verbal_territory(all_verbal_codes),
            "competitor_positions": competitor_positions
        }

    def _map_visual_territory(self, visual_codes: List[str]) -> Dict[str, int]:
        """Map visual territory by counting code frequency."""
        from collections import Counter
        return dict(Counter(visual_codes))

    def _map_verbal_territory(self, verbal_codes: List[str]) -> Dict[str, int]:
        """Map verbal territory by counting code frequency."""
        from collections import Counter
        return dict(Counter(verbal_codes))

    def _determine_cluster(self, competitor_data: Dict[str, List[str]]) -> str:
        """Determine which positioning cluster a competitor belongs to."""
        visual_codes = competitor_data.get("visual_codes", [])
        verbal_codes = competitor_data.get("verbal_codes", [])

        # Simple clustering logic
        if "minimalist" in visual_codes and "luxury" in verbal_codes:
            return "luxury_minimalist"
        elif "colorful" in visual_codes and "fun" in verbal_codes:
            return "playful_accessible"
        elif "natural" in visual_codes and "sustainable" in verbal_codes:
            return "sustainable_conscious"
        elif "luxury" in verbal_codes or "premium" in verbal_codes:
            return "premium_traditional"
        elif "innovative" in verbal_codes:
            return "modern_innovative"
        else:
            return "other"

    async def identify_white_space(
        self,
        competitors_data: Dict[str, Dict[str, List[str]]]
    ) -> List[Dict[str, Any]]:
        """
        Identify positioning white space opportunities.

        Args:
            competitors_data: Dict mapping competitor names to their codes

        Returns:
            List of white space opportunities
        """
        self.logger.info("Identifying positioning white space")

        # Build semiotic map first
        semiotic_map = await self.build_semiotic_map(competitors_data)

        # Identify crowded territories
        visual_territory = semiotic_map["visual_territory"]
        verbal_territory = semiotic_map["verbal_territory"]

        # Find codes that are underrepresented
        all_possible_visual = ["minimalist", "maximalist", "colorful", "monochrome",
                               "organic", "geometric", "warm_tones", "cool_tones",
                               "playful", "serious", "natural", "urban"]

        all_possible_verbal = ["luxury", "accessible", "fun", "serious",
                               "sustainable", "innovative", "traditional", "modern",
                               "exclusive", "inclusive", "premium", "value"]

        # Calculate white space
        white_space = []

        for visual in all_possible_visual:
            for verbal in all_possible_verbal:
                visual_count = visual_territory.get(visual, 0)
                verbal_count = verbal_territory.get(verbal, 0)

                # If both are low or zero, it's white space
                if visual_count <= 1 and verbal_count <= 1:
                    differentiation_score = 1.0 - (visual_count + verbal_count) / (2 * len(competitors_data))

                    white_space.append({
                        "visual_opportunity": visual,
                        "verbal_opportunity": verbal,
                        "strategic_rationale": f"Combine {visual} aesthetic with {verbal} messaging for unique positioning",
                        "differentiation_score": differentiation_score
                    })

        # Sort by differentiation score
        white_space.sort(key=lambda x: x["differentiation_score"], reverse=True)

        return white_space[:10]  # Top 10 opportunities

    async def analyze_positioning(
        self,
        competitor_name: str,
        visual_codes: List[str],
        verbal_codes: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze how a competitor is positioned semiotically.

        Args:
            competitor_name: Name of competitor
            visual_codes: Visual codes for this competitor
            verbal_codes: Verbal codes for this competitor

        Returns:
            Positioning analysis
        """
        visual_identity = self._summarize_visual_identity(visual_codes)
        verbal_identity = self._summarize_verbal_identity(verbal_codes)
        overall_positioning = self._determine_cluster({
            "visual_codes": visual_codes,
            "verbal_codes": verbal_codes
        })

        return {
            "visual_identity": visual_identity,
            "verbal_identity": verbal_identity,
            "overall_positioning": overall_positioning
        }

    def _summarize_visual_identity(self, visual_codes: List[str]) -> str:
        """Summarize visual identity from codes."""
        if not visual_codes:
            return "undefined"

        dominant_codes = visual_codes[:3]  # Top 3
        return f"{', '.join(dominant_codes)} aesthetic"

    def _summarize_verbal_identity(self, verbal_codes: List[str]) -> str:
        """Summarize verbal identity from codes."""
        if not verbal_codes:
            return "undefined"

        dominant_codes = verbal_codes[:3]  # Top 3
        return f"{', '.join(dominant_codes)} messaging"

    async def compare_brand_to_market(
        self,
        brand_data: Dict[str, List[str]],
        competitors_data: Dict[str, Dict[str, List[str]]]
    ) -> Dict[str, Any]:
        """
        Compare brand positioning against competitive market.

        Args:
            brand_data: Brand's visual and verbal codes
            competitors_data: Competitors' codes

        Returns:
            Comparison analysis
        """
        self.logger.info("Comparing brand to competitive market")

        similarity_scores = {}
        for competitor, comp_data in competitors_data.items():
            score = self._calculate_similarity(brand_data, comp_data)
            similarity_scores[competitor] = score

        # Find differentiation areas
        differentiation_areas = self._find_differentiation(brand_data, competitors_data)

        # Identify competitive advantage
        competitive_advantage = self._identify_competitive_advantage(
            brand_data, competitors_data, similarity_scores
        )

        return {
            "similarity_scores": similarity_scores,
            "differentiation_areas": differentiation_areas,
            "competitive_advantage": competitive_advantage
        }

    def _calculate_similarity(
        self,
        brand_data: Dict[str, List[str]],
        competitor_data: Dict[str, List[str]]
    ) -> float:
        """Calculate similarity score between brand and competitor."""
        brand_visual = set(brand_data.get("visual_codes", []))
        brand_verbal = set(brand_data.get("verbal_codes", []))

        comp_visual = set(competitor_data.get("visual_codes", []))
        comp_verbal = set(competitor_data.get("verbal_codes", []))

        # Jaccard similarity
        visual_overlap = len(brand_visual.intersection(comp_visual))
        visual_union = len(brand_visual.union(comp_visual))

        verbal_overlap = len(brand_verbal.intersection(comp_verbal))
        verbal_union = len(brand_verbal.union(comp_verbal))

        if visual_union == 0 and verbal_union == 0:
            return 0.0

        visual_sim = visual_overlap / visual_union if visual_union > 0 else 0
        verbal_sim = verbal_overlap / verbal_union if verbal_union > 0 else 0

        return (visual_sim + verbal_sim) / 2

    def _find_differentiation(
        self,
        brand_data: Dict[str, List[str]],
        competitors_data: Dict[str, Dict[str, List[str]]]
    ) -> List[str]:
        """Find areas where brand is differentiated."""
        brand_visual = set(brand_data.get("visual_codes", []))
        brand_verbal = set(brand_data.get("verbal_codes", []))

        # Aggregate all competitor codes
        all_comp_visual = set()
        all_comp_verbal = set()

        for comp_data in competitors_data.values():
            all_comp_visual.update(comp_data.get("visual_codes", []))
            all_comp_verbal.update(comp_data.get("verbal_codes", []))

        # Find unique codes
        unique_visual = brand_visual - all_comp_visual
        unique_verbal = brand_verbal - all_comp_verbal

        differentiation = []
        differentiation.extend([f"Visual: {code}" for code in unique_visual])
        differentiation.extend([f"Verbal: {code}" for code in unique_verbal])

        return differentiation

    def _identify_competitive_advantage(
        self,
        brand_data: Dict[str, List[str]],
        competitors_data: Dict[str, Dict[str, List[str]]],
        similarity_scores: Dict[str, float]
    ) -> str:
        """Identify competitive advantage based on positioning."""
        # If brand is very different from all competitors (low similarity)
        avg_similarity = sum(similarity_scores.values()) / len(similarity_scores) if similarity_scores else 0

        if avg_similarity < 0.3:
            return "Highly differentiated positioning - unique in market"
        elif avg_similarity < 0.5:
            return "Moderately differentiated - clear positioning against competitors"
        elif avg_similarity < 0.7:
            return "Similar to competitors - need to amplify unique elements"
        else:
            return "Very similar to competitors - high risk of commoditization"

    async def generate_insights(
        self,
        competitors_data: Dict[str, Dict[str, List[str]]]
    ) -> Dict[str, Any]:
        """
        Generate actionable semiotic insights.

        Args:
            competitors_data: Competitor positioning data

        Returns:
            Insights about crowded/empty territories and recommendations
        """
        semiotic_map = await self.build_semiotic_map(competitors_data)

        # Identify crowded territories
        visual_counts = semiotic_map["visual_territory"]
        verbal_counts = semiotic_map["verbal_territory"]

        crowded_visual = [code for code, count in visual_counts.items() if count >= 2]
        crowded_verbal = [code for code, count in verbal_counts.items() if count >= 2]

        crowded_territories = crowded_visual + crowded_verbal

        # Identify empty territories
        white_space = await self.identify_white_space(competitors_data)
        empty_territories = [
            f"{opp['visual_opportunity']} + {opp['verbal_opportunity']}"
            for opp in white_space[:5]
        ]

        # Generate recommendations
        recommended_positioning = []
        for opp in white_space[:3]:
            recommended_positioning.append({
                "visual": opp["visual_opportunity"],
                "verbal": opp["verbal_opportunity"],
                "rationale": opp["strategic_rationale"],
                "differentiation": opp["differentiation_score"]
            })

        return {
            "crowded_territories": crowded_territories,
            "empty_territories": empty_territories,
            "recommended_positioning": recommended_positioning
        }
