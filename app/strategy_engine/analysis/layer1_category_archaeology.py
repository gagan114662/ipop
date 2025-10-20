"""Layer 1: Category Archaeology

This layer analyzes brands to uncover:
- True functional, emotional, and social categories (beyond stated category)
- Category maturity stage
- Real competitors (often non-obvious)

Uses keyword heuristics for basic categorization and Claude API for complex analysis.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from app.strategy_engine.analysis.models import CategoryAnalysis, MaturityStage

logger = logging.getLogger(__name__)


class CategoryArchaeology:
    """Analyzes brand category positioning and identifies real competition."""

    # Currency conversion rates (to USD)
    CURRENCY_RATES = {
        "USD": 1.0,
        "INR": 0.012,  # 1 INR ≈ $0.012
        "EUR": 1.08,   # 1 EUR ≈ $1.08
        "GBP": 1.27,   # 1 GBP ≈ $1.27
        "JPY": 0.0067, # 1 JPY ≈ $0.0067
        "AUD": 0.65,   # 1 AUD ≈ $0.65
    }

    # Category-specific luxury price thresholds (in USD)
    # These represent "luxury/status" entry points by category
    CATEGORY_LUXURY_THRESHOLDS = {
        "watches": 3000,
        "fashion": 500,
        "ethnic wear": 400,
        "ethnic menswear": 400,
        "jewelry": 2000,
        "handbags": 1000,
        "shoes": 400,
        "accessories": 300,
        "home decor": 500,
        "furniture": 2000,
        "default": 500
    }

    # Regional purchasing power adjustments (multiplier)
    REGIONAL_ADJUSTMENTS = {
        "India": 0.4,  # $100 in India ≈ $250 purchasing power in USA
        "China": 0.5,
        "United States": 1.0,
        "Europe": 1.1,
        "UK": 1.1,
        "Japan": 1.2,
        "default": 1.0
    }

    def __init__(self):
        """Initialize the category archaeology analyzer."""
        self.logger = logger

    async def _parse_price(self, price_str: str, default_currency: str = "USD") -> float:
        """
        Parse price string and extract numeric value.

        Args:
            price_str: Price string (e.g., "₹67,000", "$1,299.99", "5500")
            default_currency: Default currency if not found in string

        Returns:
            Float price value
        """
        if isinstance(price_str, (int, float)):
            return float(price_str)

        # Remove currency symbols and commas
        cleaned = re.sub(r'[₹$€£¥,]', '', str(price_str))

        try:
            return float(cleaned)
        except ValueError:
            self.logger.warning(f"Failed to parse price: {price_str}")
            return 0.0

    def _detect_currency(self, price_str: str, brand_data: Dict) -> str:
        """
        Detect currency from price string or brand data.

        Args:
            price_str: Price string
            brand_data: Brand data dictionary

        Returns:
            Currency code (USD, INR, EUR, etc.)
        """
        # Check explicit currency field
        if "currency" in brand_data:
            return brand_data["currency"].upper()

        # Detect from price string
        currency_symbols = {
            "₹": "INR",
            "$": "USD",
            "€": "EUR",
            "£": "GBP",
            "¥": "JPY",
        }

        for symbol, code in currency_symbols.items():
            if symbol in price_str:
                return code

        # Check region
        region = brand_data.get("region", "").lower()
        if "india" in region:
            return "INR"
        elif "europe" in region:
            return "EUR"
        elif "uk" in region or "britain" in region:
            return "GBP"
        elif "japan" in region:
            return "JPY"

        # Default to USD
        return "USD"

    def _convert_to_usd(self, price: float, currency: str) -> float:
        """
        Convert price to USD for comparison.

        Args:
            price: Price value
            currency: Currency code

        Returns:
            Price in USD
        """
        rate = self.CURRENCY_RATES.get(currency.upper(), 1.0)
        return price * rate

    def _get_adjusted_price(self, price_usd: float, region: str, category: str) -> float:
        """
        Adjust USD price for regional purchasing power.

        Args:
            price_usd: Price in USD
            region: Region name
            category: Product category

        Returns:
            Adjusted price for fair comparison
        """
        adjustment = self.REGIONAL_ADJUSTMENTS.get(region, self.REGIONAL_ADJUSTMENTS["default"])

        # Safety check: prevent division by zero
        if adjustment == 0 or adjustment is None:
            self.logger.warning(f"Invalid adjustment factor {adjustment} for region {region}, using default 1.0")
            adjustment = 1.0

        # Divide by adjustment because lower adjustment = higher purchasing power
        return price_usd / adjustment

    def _get_luxury_threshold(self, category: str) -> float:
        """
        Get luxury price threshold for category.

        Args:
            category: Product category

        Returns:
            Luxury threshold in USD
        """
        category_lower = category.lower()
        for key, threshold in self.CATEGORY_LUXURY_THRESHOLDS.items():
            if key in category_lower:
                return threshold
        return self.CATEGORY_LUXURY_THRESHOLDS["default"]

    async def _extract_prices(self, brand_data: Dict) -> Tuple[float, float]:
        """
        Extract and normalize prices from brand data.

        Args:
            brand_data: Brand data dictionary

        Returns:
            Tuple of (min_price_usd, max_price_usd) adjusted for region
        """
        prices = []
        products = brand_data.get("products", [])
        region = brand_data.get("region", "")
        category = brand_data.get("category_stated", "")

        # Extract prices from products
        for product in products:
            price_str = product.get("price", "")
            if price_str:
                currency = self._detect_currency(str(price_str), brand_data)
                price = await self._parse_price(str(price_str), currency)
                price_usd = self._convert_to_usd(price, currency)
                adjusted_price = self._get_adjusted_price(price_usd, region, category)
                prices.append(adjusted_price)

        # Also check for price_range field
        if "price_range" in brand_data:
            price_range = brand_data["price_range"]
            if isinstance(price_range, (list, tuple)) and len(price_range) >= 2:
                # Assume price_range is already in brand's currency
                currency = brand_data.get("currency", "USD")
                for price_val in price_range[:2]:
                    if price_val > 0:
                        price_usd = self._convert_to_usd(float(price_val), currency)
                        adjusted_price = self._get_adjusted_price(price_usd, region, category)
                        prices.append(adjusted_price)

        if not prices:
            return (0.0, 0.0)

        return (min(prices), max(prices))

    async def analyze(self, brand_data: Dict) -> CategoryAnalysis:
        """
        Analyze brand and determine real categories.

        Args:
            brand_data: Dictionary containing:
                - products: List of product dicts with name/description
                - category_stated: How brand describes itself
                - price_range: Tuple of (min, max) prices
                - brand_messaging: Brand messaging/tagline

        Returns:
            CategoryAnalysis with functional, emotional, and social categories
        """
        self.logger.info(f"Analyzing category for brand: {brand_data.get('category_stated')}")

        # Extract product descriptions
        products = brand_data.get("products", [])
        product_text = " ".join([
            f"{p.get('name', '')} {p.get('description', '')}"
            for p in products
        ])
        messaging = brand_data.get("brand_messaging", "")
        combined_text = f"{product_text} {messaging}".lower()

        # Identify functional category (what job it actually does)
        functional_category = self._identify_functional_category(combined_text)

        # Identify emotional category (how it makes them feel)
        emotional_category = await self._identify_emotional_category(combined_text, brand_data)

        # Identify social category (social job it performs)
        social_category = await self._identify_social_category(combined_text, brand_data)

        # Determine maturity stage (would require market data in real implementation)
        # For now, use heuristics based on price range and messaging
        estimated_market_data = self._estimate_market_data(brand_data)
        maturity = await self.determine_maturity(estimated_market_data)

        # Generate strategic implication
        strategic_implication = self._generate_strategic_implication(
            functional_category,
            emotional_category,
            social_category,
            maturity
        )

        # Identify real competitors
        category_data = {
            "stated_category": brand_data.get("category_stated"),
            "functional_category": functional_category,
            "emotional_job": emotional_category,
            "social_job": social_category
        }
        real_competitors = await self.identify_real_competitors(category_data)

        return CategoryAnalysis(
            stated_category=brand_data.get("category_stated", "Unknown"),
            functional_category=functional_category,
            emotional_category=emotional_category,
            social_category=social_category,
            maturity=maturity,
            strategic_implication=strategic_implication,
            real_competitors=real_competitors
        )

    def _identify_functional_category(self, text: str) -> Optional[str]:
        """Identify the functional job the product serves."""
        functional_keywords = {
            "craftsmanship": ["handmade", "artisan", "crafted", "embroidery", "weaving", "hand", "craftsmanship", "artisanal"],
            "comfort": ["comfort", "soft", "breathable", "fit", "wearable", "easy wear"],
            "durability": ["durable", "lasting", "quality", "resilient", "sturdy", "long-lasting"],
            "protection": ["protect", "weather", "warm", "waterproof", "shield"],
            "time_management": ["time", "schedule", "punctual", "precision", "timekeeping"],
            "status_symbols": ["luxury", "premium", "exclusive", "prestige", "heritage"],
            "self_expression": ["unique", "personal", "style", "individual", "custom"],
            "convenience": ["easy", "simple", "quick", "convenient", "efficient"],
            "sustainability": ["sustainable", "eco", "recycled", "carbon neutral", "planet", "green"],
            "health_tracking": ["fitness", "health", "steps", "heart", "activity"],
            "communication": ["connect", "message", "call", "notify", "alert"]
        }

        scores = {}
        for category, keywords in functional_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[category] = score

        if scores:
            return max(scores, key=scores.get)
        return "general_utility"

    async def _identify_emotional_category(self, text: str, brand_data: Dict) -> Optional[str]:
        """Identify the emotional job the product serves."""
        emotional_keywords = {
            "confidence": ["confident", "empowered", "strong", "bold"],
            "belonging": ["community", "tribe", "belong", "together", "us"],
            "aspiration": ["dream", "achieve", "success", "goal", "better"],
            "nostalgia": ["heritage", "classic", "timeless", "tradition", "legacy"],
            "adventure": ["explore", "discover", "journey", "adventure", "experience"],
            "peace_of_mind": ["safe", "secure", "reliable", "trust", "dependable"],
            "virtue_signaling": ["sustainable", "ethical", "conscious", "responsible", "planet"],
            "status": ["luxury", "premium", "exclusive", "elite", "prestigious", "celebrity", "designer"]
        }

        scores = {}
        for category, keywords in emotional_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[category] = score

        # Use category-aware, currency-aware pricing to determine status
        min_price, max_price = await self._extract_prices(brand_data)
        category = brand_data.get("category_stated", "")
        luxury_threshold = self._get_luxury_threshold(category)

        # If max price exceeds luxury threshold for this category, boost status score
        if max_price > luxury_threshold:
            scores["status"] = scores.get("status", 0) + 3
        elif max_price > luxury_threshold * 0.5:
            # Mid-premium range
            scores["status"] = scores.get("status", 0) + 1
            scores["aspiration"] = scores.get("aspiration", 0) + 1

        if scores:
            return max(scores, key=scores.get)
        return "general_satisfaction"

    async def _identify_social_category(self, text: str, brand_data: Dict) -> Optional[str]:
        """Identify the social job the product serves."""
        social_keywords = {
            "stand_out": ["stand out", "different", "unique", "exclusive", "rare", "one of a kind"],
            "signal_wealth": ["luxury", "premium", "expensive", "prestigious", "elite", "high-end"],
            "cultural_pride": ["heritage", "tradition", "cultural", "authentic", "roots", "legacy"],
            "family_pride": ["family", "wedding", "ceremony", "occasion", "celebration"],
            "identity_markers": ["statement", "identity", "who i am", "express", "define"],
            "conversation_starters": ["unusual", "story", "interesting", "remarkable"],
            "tribe_membership": ["community", "movement", "belong", "tribe", "group"],
            "social_proof": ["popular", "trending", "everyone", "influencer", "viral"],
            "differentiation": ["different", "exclusive"]
        }

        scores = {}
        for category, keywords in social_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[category] = score

        # Use pricing to infer social job
        min_price, max_price = await self._extract_prices(brand_data)
        category = brand_data.get("category_stated", "")
        luxury_threshold = self._get_luxury_threshold(category)

        # High-priced items in ethnic/fashion likely signal wealth or status
        if max_price > luxury_threshold:
            scores["signal_wealth"] = scores.get("signal_wealth", 0) + 2
            scores["stand_out"] = scores.get("stand_out", 0) + 1

        # Ethnic/cultural categories likely involve cultural pride
        if any(keyword in category.lower() for keyword in ["ethnic", "traditional", "cultural", "wedding"]):
            scores["cultural_pride"] = scores.get("cultural_pride", 0) + 2
            scores["family_pride"] = scores.get("family_pride", 0) + 1

        if scores:
            return max(scores, key=scores.get)
        return "general_acceptance"

    def _estimate_market_data(self, brand_data: Dict) -> Dict:
        """Estimate market data based on brand characteristics."""
        price_range = brand_data.get("price_range", (0, 0))
        category = brand_data.get("category_stated", "").lower()

        # Heuristics for market estimation
        if "watch" in category.lower():
            # Watch market is commoditized
            return {
                "competitor_count": 500,
                "price_variance": 0.15,
                "innovation_rate": "low",
                "market_growth": 0.03
            }
        elif "sustainable" in category.lower() or "eco" in category.lower():
            # Sustainability is growing market
            return {
                "competitor_count": 85,
                "price_variance": 0.28,
                "innovation_rate": "medium",
                "market_growth": 0.18
            }
        else:
            # Default to mature market
            return {
                "competitor_count": 200,
                "price_variance": 0.20,
                "innovation_rate": "medium",
                "market_growth": 0.08
            }

    async def determine_maturity(self, market_data: Dict) -> MaturityStage:
        """
        Determine category maturity stage.

        Args:
            market_data: Dictionary containing:
                - competitor_count: Number of competitors
                - price_variance: Price variance (0-1)
                - innovation_rate: "low", "medium", "high"
                - market_growth: Growth rate (0-1)

        Returns:
            MaturityStage with stage and strategic implication
        """
        competitor_count = market_data.get("competitor_count", 100)
        price_variance = market_data.get("price_variance", 0.2)
        innovation_rate = market_data.get("innovation_rate", "medium")
        market_growth = market_data.get("market_growth", 0.1)

        # Scoring logic
        if competitor_count < 30 and market_growth > 0.25:
            stage = "early_innovation"
            implication = "Focus on category creation, education, and defining standards. Be the leader who shapes the category."
        elif competitor_count < 100 and market_growth > 0.15:
            stage = "growth"
            implication = "Focus on differentiation and capturing market share. Speed and scale matter. Build brand moat now."
        elif competitor_count > 300 and price_variance < 0.15:
            stage = "commoditized"
            implication = "Compete on meaning, not features. Create cultural relevance. Build brand as a belief system or lifestyle."
        else:
            stage = "mature"
            implication = "Focus on brand strength and customer loyalty. Innovation at edges. Efficiency in core operations."

        self.logger.info(f"Market maturity determined: {stage}")

        return MaturityStage(
            stage=stage,
            strategic_implication=implication
        )

    async def identify_real_competitors(self, category_data: Dict) -> List[str]:
        """
        Identify real (often non-obvious) competitors.

        Real competitors serve the same job, not just the same category.

        Args:
            category_data: Dictionary containing:
                - stated_category: How brand describes itself
                - functional_category: Real functional job
                - emotional_job: Emotional job served
                - social_job: Social job served

        Returns:
            List of real competitor categories
        """
        emotional_job = category_data.get("emotional_job")
        social_job = category_data.get("social_job")
        functional_category = category_data.get("functional_category")

        competitors = set()

        # Add stated category competitors
        stated = category_data.get("stated_category", "")
        if stated:
            competitors.add(stated)

        # Emotional job competitors
        if emotional_job == "status":
            competitors.update([
                "Luxury jewelry",
                "Designer fashion",
                "Luxury cars",
                "Premium tech devices",
                "Fine dining experiences"
            ])
        elif emotional_job == "virtue_signaling":
            competitors.update([
                "Sustainable fashion brands",
                "Eco-friendly products",
                "Plant-based food brands",
                "Electric vehicles",
                "Ethical investment platforms"
            ])
        elif emotional_job == "nostalgia":
            competitors.update([
                "Heritage brands",
                "Vintage products",
                "Classic designs",
                "Retro experiences"
            ])

        # Social job competitors
        if social_job == "identity_markers":
            competitors.update([
                "Fashion brands",
                "Lifestyle brands",
                "Subculture products",
                "Statement accessories"
            ])
        elif social_job == "tribe_membership":
            competitors.update([
                "Community-driven brands",
                "Movement brands",
                "Membership organizations",
                "Lifestyle communities"
            ])

        # Functional category competitors
        if functional_category == "time_management":
            competitors.update([
                "Smartphones",
                "Smart watches",
                "Calendar apps",
                "Productivity tools"
            ])
        elif functional_category == "status_symbols":
            competitors.update([
                "Luxury goods",
                "Premium brands across categories",
                "Exclusive experiences",
                "High-end services"
            ])

        # Remove stated category to show non-obvious competitors
        competitors.discard(stated)

        # Convert to list and limit to top competitors
        competitor_list = list(competitors)[:8]

        self.logger.info(f"Identified {len(competitor_list)} real competitors")

        return competitor_list

    def _generate_strategic_implication(
        self,
        functional: Optional[str],
        emotional: Optional[str],
        social: Optional[str],
        maturity: MaturityStage
    ) -> str:
        """Generate strategic implication from category analysis."""
        implications = []

        if functional and emotional and functional != emotional:
            implications.append(
                f"True competition is in {emotional}, not {functional}. "
                f"Focus brand building on emotional dimension."
            )

        implications.append(maturity.strategic_implication)

        if social in ["identity_markers", "tribe_membership"]:
            implications.append(
                "Brand as badge. Community and culture are your moat, not product features."
            )

        return " ".join(implications)
