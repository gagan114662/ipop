"""Layer 3: Framework Dialectics

This layer finds strategic tensions through contradiction analysis:
- Product vs User: What brand promises vs what users actually want
- Space vs Time: Market positioning vs purchase timing
- UX vs Product: Desired experience vs actual product

Contradictions reveal human truths that drive better strategy.
"""

import logging
from typing import Dict, List
from app.strategy_engine.analysis.models import Tension

logger = logging.getLogger(__name__)


class FrameworkDialectics:
    """Finds strategic tensions through dialectical analysis."""

    def __init__(self):
        """Initialize the framework dialectics analyzer."""
        self.logger = logger

    def _extract_product_data(self, brand_data: Dict) -> Dict:
        """
        Extract product data from raw brand data.

        Args:
            brand_data: Raw brand data from scraping

        Returns:
            Dictionary with product_promise, messaging_focus
        """
        # Extract product promise from brand messaging
        product_promise = brand_data.get("brand_messaging", "")

        # If no explicit messaging, infer from products
        if not product_promise:
            products = brand_data.get("products", [])
            if products:
                # Extract common themes from product descriptions
                descriptions = [p.get("description", "") for p in products if p.get("description")]
                if descriptions:
                    product_promise = descriptions[0]  # Use first description as proxy

        # Extract messaging focus from product keywords
        messaging_focus = []
        products = brand_data.get("products", [])
        for product in products[:3]:  # Top 3 products
            name = product.get("name", "")
            desc = product.get("description", "")
            if name:
                messaging_focus.append(name)
            elif desc:
                messaging_focus.append(desc)

        return {
            "product_promise": product_promise or "premium quality products",
            "messaging_focus": messaging_focus or ["quality", "design"]
        }

    def _extract_user_data(self, brand_data: Dict) -> Dict:
        """
        Extract user behavior data from brand signals.

        Args:
            brand_data: Raw brand data

        Returns:
            Dictionary with purchase_drivers, stated_values, actual_behavior
        """
        category = brand_data.get("category_stated", "").lower()
        price_range = brand_data.get("price_range", (0, 0))
        max_price = max(price_range) if price_range else 0

        # Infer purchase drivers from category and price
        purchase_drivers = []
        stated_values = []

        # High-priced items = status/quality drivers
        if max_price > 50000 or any(keyword in category for keyword in ["luxury", "premium", "designer"]):
            purchase_drivers = ["status", "quality", "social proof"]
            stated_values = ["craftsmanship", "heritage"]
        elif any(keyword in category for keyword in ["wedding", "ceremony", "formal"]):
            purchase_drivers = ["occasion", "confidence", "status"]
            stated_values = ["tradition", "quality"]
        else:
            purchase_drivers = ["quality", "value", "style"]
            stated_values = ["quality", "durability"]

        # Infer actual behavior from category
        actual_behavior = f"buys for {purchase_drivers[0] if purchase_drivers else 'value'}"

        return {
            "purchase_drivers": purchase_drivers,
            "stated_values": stated_values,
            "actual_behavior": actual_behavior
        }

    def _extract_space_data(self, brand_data: Dict) -> Dict:
        """
        Extract market space data from brand signals.

        Args:
            brand_data: Raw brand data

        Returns:
            Dictionary with market_position, price_point, distribution
        """
        price_range = brand_data.get("price_range", (0, 0))
        category = brand_data.get("category_stated", "").lower()
        max_price = max(price_range) if price_range else 0

        # Infer market position from price
        if max_price > 50000:
            market_position = "premium/luxury"
            price_point = "high-end"
        elif max_price > 20000:
            market_position = "upper-mid market"
            price_point = "premium"
        else:
            market_position = "mid-market"
            price_point = "accessible"

        return {
            "market_position": market_position,
            "price_point": price_point,
            "distribution": brand_data.get("distribution", "selective")
        }

    def _extract_time_data(self, brand_data: Dict) -> Dict:
        """
        Extract purchase timing data from category signals.

        Args:
            brand_data: Raw brand data

        Returns:
            Dictionary with purchase_occasion, consideration_period
        """
        category = brand_data.get("category_stated", "").lower()

        # Infer purchase occasion and consideration from category
        if any(keyword in category for keyword in ["wedding", "ceremony", "formal", "occasion"]):
            purchase_occasion = "high-stakes event"
            consideration_period = "short (2-4 weeks)"
        elif any(keyword in category for keyword in ["luxury", "designer", "premium"]):
            purchase_occasion = "planned purchase"
            consideration_period = "medium (1-3 months)"
        else:
            purchase_occasion = "regular need"
            consideration_period = "short (days to weeks)"

        return {
            "purchase_occasion": purchase_occasion,
            "consideration_period": consideration_period
        }

    def _extract_ux_data(self, brand_data: Dict) -> Dict:
        """
        Extract desired UX from category and price signals.

        Args:
            brand_data: Raw brand data

        Returns:
            Dictionary with desired_experience, emotional_goal
        """
        category = brand_data.get("category_stated", "").lower()
        price_range = brand_data.get("price_range", (0, 0))
        max_price = max(price_range) if price_range else 0

        # Infer desired experience
        if max_price > 50000:
            desired_experience = "luxurious and exclusive"
            emotional_goal = "feel special and confident"
        elif "wedding" in category or "ceremony" in category:
            desired_experience = "memorable and stress-free"
            emotional_goal = "feel confident on big day"
        else:
            desired_experience = "simple and convenient"
            emotional_goal = "feel satisfied with purchase"

        return {
            "desired_experience": desired_experience,
            "emotional_goal": emotional_goal
        }

    async def analyze_brand(self, brand_data: Dict) -> List[Tension]:
        """
        Analyze brand and extract all tensions from raw data.

        This is the main entry point for Layer 3 analysis.

        Args:
            brand_data: Raw brand data from scraping (products, messaging, category, prices)

        Returns:
            List of Tension objects
        """
        self.logger.info("Analyzing brand for strategic tensions")

        # Extract structured data from raw brand data
        product_data = self._extract_product_data(brand_data)
        user_data = self._extract_user_data(brand_data)
        space_data = self._extract_space_data(brand_data)
        time_data = self._extract_time_data(brand_data)
        ux_data = self._extract_ux_data(brand_data)

        # Build analysis structure
        brand_analysis = {
            "product": product_data,
            "user": user_data,
            "space": space_data,
            "time": time_data,
            "ux": ux_data
        }

        # Find all tensions
        return await self.find_all_tensions(brand_analysis)

    async def find_product_user_tension(
        self,
        product_data: Dict,
        user_data: Dict
    ) -> Tension:
        """
        Find tension between product promise and user behavior.

        The gap between what brands say and what users actually want.

        Args:
            product_data: Dictionary with product_promise, messaging_focus
            user_data: Dictionary with purchase_drivers, stated_values, actual_behavior

        Returns:
            Tension object with contradiction, human_truth, strategic_implication
        """
        self.logger.info("Finding product-user tension")

        product_promise = product_data.get("product_promise", "")
        messaging = product_data.get("messaging_focus", [])

        purchase_drivers = user_data.get("purchase_drivers", [])
        stated_values = user_data.get("stated_values", [])
        actual_behavior = user_data.get("actual_behavior", "")

        # Analyze the gap
        contradiction = self._identify_contradiction(
            promise=product_promise,
            messaging=messaging,
            drivers=purchase_drivers,
            behavior=actual_behavior
        )

        # Extract human truth
        human_truth = self._extract_human_truth(
            stated=stated_values,
            actual=purchase_drivers,
            behavior=actual_behavior
        )

        # Generate strategic implication
        strategic_implication = self._generate_strategic_implication(
            contradiction=contradiction,
            human_truth=human_truth,
            dimension="product_user"
        )

        return Tension(
            tension_type="product_user",
            contradiction=contradiction,
            human_truth=human_truth,
            strategic_implication=strategic_implication
        )

    async def find_space_time_tension(
        self,
        space_data: Dict,
        time_data: Dict
    ) -> Tension:
        """
        Find tension between market space and purchase timing.

        High-end positioning but impulse purchase behavior, for example.

        Args:
            space_data: Dictionary with market_position, price_point, distribution
            time_data: Dictionary with purchase_occasion, consideration_period

        Returns:
            Tension object
        """
        self.logger.info("Finding space-time tension")

        market_position = space_data.get("market_position", "") or "mid-market"
        price_point = space_data.get("price_point", "") or "accessible"

        purchase_occasion = time_data.get("purchase_occasion", "") or "regular need"
        consideration_period = time_data.get("consideration_period", "") or "short"

        # Find contradiction
        if "premium" in market_position.lower() or "luxury" in market_position.lower():
            if "impulse" in purchase_occasion.lower() or "short" in consideration_period.lower():
                contradiction = (
                    f"Positioned as {market_position} ({price_point} price), "
                    f"but purchased as {purchase_occasion} with {consideration_period} consideration"
                )
                human_truth = (
                    "They justify the purchase after the fact. "
                    "The emotional decision happens instantly, "
                    "then they rationalize it with your premium positioning."
                )
                strategic_implication = (
                    "Lead with emotional triggers, not rational features. "
                    "Premium positioning is the rationalization tool, not the purchase driver. "
                    "Create desire first, justify quality second."
                )
            else:
                contradiction = f"Premium positioning aligns with deliberate {purchase_occasion} purchase"
                human_truth = (
                    "They research thoroughly because the investment feels significant. "
                    "They're buying peace of mind as much as the product."
                )
                strategic_implication = (
                    "Provide extensive information and social proof. "
                    "Help them feel confident in their considered decision."
                )
        else:
            contradiction = f"Market position ({market_position}) matches purchase timing ({purchase_occasion})"
            human_truth = "Straightforward value exchange without emotional complexity"
            strategic_implication = "Focus on clear value communication and convenience"

        return Tension(
            tension_type="space_time",
            contradiction=contradiction,
            human_truth=human_truth,
            strategic_implication=strategic_implication
        )

    async def find_ux_product_tension(
        self,
        ux_data: Dict,
        product_data: Dict
    ) -> Tension:
        """
        Find tension between desired experience and product reality.

        Want simplicity but product is complex, for example.

        Args:
            ux_data: Dictionary with desired_experience, emotional_goal
            product_data: Dictionary with actual_complexity, feature_count

        Returns:
            Tension object
        """
        self.logger.info("Finding UX-product tension")

        desired_experience = ux_data.get("desired_experience", "")
        emotional_goal = ux_data.get("emotional_goal", "")

        actual_complexity = product_data.get("actual_complexity", "")
        feature_count = product_data.get("feature_count", "")

        # Find contradiction
        if "simple" in desired_experience.lower() or "easy" in desired_experience.lower():
            if "high" in actual_complexity.lower() or "extensive" in str(feature_count).lower():
                contradiction = (
                    f"Users want {desired_experience} for {emotional_goal}, "
                    f"but product has {actual_complexity} with {feature_count} features"
                )
                human_truth = (
                    "They want the outcome without the effort. "
                    "They'll pay for simplicity, not complexity. "
                    "Every feature you add is a reason not to buy."
                )
                strategic_implication = (
                    "Hide complexity behind simple interface. "
                    "Market the outcome, not the features. "
                    "Make power optional, simplicity default."
                )
            else:
                contradiction = f"Desired {desired_experience} matches actual product simplicity"
                human_truth = "Simplicity is the feature"
                strategic_implication = "Lead with ease of use and quick value delivery"
        else:
            contradiction = f"Experience expectation ({desired_experience}) aligns with product"
            human_truth = "Users expect and appreciate the depth"
            strategic_implication = "Showcase capabilities and power for the right audience"

        return Tension(
            tension_type="ux_product",
            contradiction=contradiction,
            human_truth=human_truth,
            strategic_implication=strategic_implication
        )

    async def find_all_tensions(self, brand_analysis: Dict) -> List[Tension]:
        """
        Find all tensions across all dimension pairs.

        Args:
            brand_analysis: Dictionary with product, user, space, time, ux data

        Returns:
            List of Tension objects
        """
        self.logger.info("Finding all strategic tensions")

        tensions = []

        # Product-User tension
        if "product" in brand_analysis and "user" in brand_analysis:
            product_user_tension = await self.find_product_user_tension(
                brand_analysis["product"],
                brand_analysis["user"]
            )
            tensions.append(product_user_tension)

        # Space-Time tension
        if "space" in brand_analysis and "time" in brand_analysis:
            space_time_tension = await self.find_space_time_tension(
                brand_analysis["space"],
                brand_analysis["time"]
            )
            tensions.append(space_time_tension)

        # UX-Product tension
        if "ux" in brand_analysis and "product" in brand_analysis:
            ux_product_tension = await self.find_ux_product_tension(
                brand_analysis["ux"],
                brand_analysis["product"]
            )
            tensions.append(ux_product_tension)

        self.logger.info(f"Found {len(tensions)} strategic tensions")
        return tensions

    def _identify_contradiction(
        self,
        promise: str,
        messaging: List[str],
        drivers: List[str],
        behavior: str
    ) -> str:
        """Identify the core contradiction."""
        # Handle empty/None promise
        if not promise or promise.lower() == "none":
            promise = messaging[0] if messaging else "premium quality"

        # Check if promise is in top drivers
        promise_lower = promise.lower()
        drivers_lower = [d.lower() for d in drivers]

        if messaging:
            primary_message = messaging[0].lower()
        else:
            primary_message = promise_lower

        # Check position of promise in purchase drivers
        if drivers_lower:
            # Check if any part of promise appears in drivers
            promise_words = promise_lower.split()
            matching_drivers = [d for d in drivers_lower if any(word in d for word in promise_words)]

            if matching_drivers:
                # Promise theme appears in drivers
                matching_driver = matching_drivers[0]
                position = drivers_lower.index(matching_driver) + 1
                if position > 1:
                    return (
                        f"Brand emphasizes {promise}, "
                        f"but users rank related needs ('{matching_driver}') as #{position} priority after {', '.join(drivers[:position-1])}"
                    )
                else:
                    return f"Brand promise ({promise}) aligns with top user priority ({drivers[0]})"
            else:
                # Promise not in drivers at all
                top_driver = drivers[0] if drivers else "value"
                return (
                    f"Brand promises {promise}, "
                    f"but users actually buy for {top_driver}"
                )
        else:
            # No driver data - use fallback
            return f"Brand emphasizes {promise} in messaging"

    def _extract_human_truth(
        self,
        stated: List[str],
        actual: List[str],
        behavior: str
    ) -> str:
        """Extract the human truth from the gap."""
        if not stated or not actual:
            return "People buy on emotion, justify with logic"

        # Find the gap
        stated_lower = [s.lower() for s in stated]
        actual_lower = [a.lower() for a in actual]

        # Check if stated values appear in actual drivers
        stated_in_actual = [s for s in stated_lower if s in actual_lower]

        if not stated_in_actual:
            # Complete mismatch
            return (
                f"They say they value {stated[0]}, "
                f"but they actually buy based on {actual[0]}. "
                f"The stated value is aspirational, the actual driver is emotional."
            )
        elif stated_lower[0] != actual_lower[0]:
            # Stated value exists but isn't #1 priority
            return (
                f"They believe in {stated[0]}, "
                f"but {actual[0]} drives the purchase decision. "
                f"Stated values are real, just not primary."
            )
        else:
            # Alignment
            return (
                f"Rare alignment: they say {stated[0]} and actually mean it. "
                f"Build trust through consistent delivery."
            )

    def _generate_strategic_implication(
        self,
        contradiction: str,
        human_truth: str,
        dimension: str
    ) -> str:
        """Generate actionable strategic implication."""
        if "buy for" in contradiction.lower() or "actually" in human_truth.lower():
            # There's a gap - focus on actual behavior
            return (
                "Message to the real driver, not the stated value. "
                "Use stated values for justification, actual drivers for desire. "
                "Create desire first, provide rationalization second."
            )
        elif "mismatch" in contradiction.lower() or "gap" in contradiction.lower():
            return (
                "Bridge the gap by positioning actual benefits within their value framework. "
                "Show how the real driver delivers on stated values."
            )
        elif "aligns" in contradiction.lower() or "alignment" in human_truth.lower():
            return (
                "Rare opportunity: stated and actual align. "
                "Amplify this value consistently. Build brand around this truth."
            )
        else:
            return (
                "Focus on emotional drivers in creative, "
                "use rational benefits for consideration phase."
            )
