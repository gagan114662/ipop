"""Layer 6: Jobs-to-be-Done

This layer identifies the actual jobs customers are hiring the product to do.
Goes beyond functional features to uncover emotional and social jobs.

Key insight: Customers don't want a drill, they want a hole in the wall.
Actually, they want to hang a picture. Actually, they want to feel proud of their home.

Mock implementation for now - will integrate real customer insight analysis later.
"""

import logging
from typing import List, Dict, Any
from app.strategy_engine.analysis.models import (
    JobsAnalysis,
    Job,
    Alternative
)

logger = logging.getLogger(__name__)


class JobsToBeDone:
    """Analyzes the jobs customers are hiring the product to do."""

    def __init__(self):
        """Initialize the jobs-to-be-done analyzer."""
        self.logger = logger

    async def analyze(
        self,
        brand_data: Dict[str, Any],
        customer_data: Dict[str, Any]
    ) -> JobsAnalysis:
        """
        Complete jobs-to-be-done analysis.

        Args:
            brand_data: Product features, positioning, marketing
            customer_data: Usage patterns, motivations, alternatives

        Returns:
            JobsAnalysis with primary job and job hierarchy
        """
        self.logger.info("Analyzing jobs-to-be-done")

        # Identify all three types of jobs
        jobs = await self.identify_jobs({**brand_data, **customer_data})

        # Rank jobs by importance
        ranked_jobs = await self.rank_jobs(customer_data)

        # Determine primary job (usually emotional or social, not functional)
        primary_job = self._determine_primary_job(jobs, ranked_jobs)

        # Find alternative solutions
        alternatives = await self.find_alternatives(primary_job)

        # Build job hierarchy
        job_hierarchy = {
            "functional": jobs.functional_job.importance,
            "emotional": jobs.emotional_job.importance,
            "social": jobs.social_job.importance
        }

        return JobsAnalysis(
            primary_job=primary_job,
            functional_job=jobs.functional_job,
            emotional_job=jobs.emotional_job,
            social_job=jobs.social_job,
            alternatives=alternatives,
            job_hierarchy=job_hierarchy
        )

    async def identify_jobs(self, data: Dict[str, Any]) -> JobsAnalysis:
        """
        Identify functional, emotional, and social jobs.

        Args:
            data: Combined brand and customer data

        Returns:
            JobsAnalysis with all three job types identified
        """
        self.logger.info("Identifying functional, emotional, and social jobs")

        # Extract functional job (what the product does)
        functional_job = self._identify_functional_job(data)

        # Extract emotional job (how customer wants to feel)
        emotional_job = self._identify_emotional_job(data)

        # Extract social job (how customer wants to be perceived)
        social_job = self._identify_social_job(data)

        # Determine which is primary
        jobs_list = [functional_job, emotional_job, social_job]
        primary_job = max(jobs_list, key=lambda j: j.importance)

        return JobsAnalysis(
            primary_job=primary_job,
            functional_job=functional_job,
            emotional_job=emotional_job,
            social_job=social_job,
            alternatives=[],
            job_hierarchy={
                "functional": functional_job.importance,
                "emotional": emotional_job.importance,
                "social": social_job.importance
            }
        )

    async def find_alternatives(self, job: Job) -> List[Alternative]:
        """
        Find alternative solutions customers consider for this job.

        Args:
            job: The job to find alternatives for

        Returns:
            List of alternative solutions
        """
        self.logger.info(f"Finding alternatives for {job.job_type} job")

        alternatives = []

        # Direct competitors (same solution to same job)
        alternatives.append(Alternative(
            name="Direct competitor products",
            category="direct_competitor",
            description=f"Other products that explicitly solve {job.description}",
            switching_cost=0.3  # Low switching cost to similar products
        ))

        # Indirect competitors (different solution to same job)
        if job.job_type == "emotional":
            alternatives.append(Alternative(
                name="Therapy or coaching",
                category="indirect_competitor",
                description="Professional help to achieve emotional outcomes",
                switching_cost=0.6  # Higher cost, different approach
            ))

        # Substitutes (completely different approach)
        alternatives.append(Alternative(
            name="DIY or alternative method",
            category="substitute",
            description="Solving the problem without the product category",
            switching_cost=0.7  # High effort to switch approach
        ))

        # Non-consumption (doing nothing)
        alternatives.append(Alternative(
            name="Non-consumption (inertia)",
            category="non-consumption",
            description="Not addressing the job at all - maintaining status quo",
            switching_cost=0.0  # Easiest option is to do nothing
        ))

        return alternatives

    async def find_alternatives_for_product(self, data: Dict[str, Any]) -> List[Alternative]:
        """
        Find alternatives specific to product data.

        Args:
            data: Product and market data

        Returns:
            List of alternatives including non-consumption
        """
        self.logger.info("Finding alternatives for product")

        alternatives = []

        # Always include non-consumption
        alternatives.append(Alternative(
            name="Non-consumption",
            category="non-consumption",
            description="Customer chooses not to solve this problem at all",
            switching_cost=0.0
        ))

        # Add other alternatives based on data
        if "alternatives" in data:
            for alt in data.get("alternatives", []):
                alternatives.append(Alternative(
                    name=alt,
                    category="indirect_competitor",
                    description=f"Alternative solution: {alt}",
                    switching_cost=0.5
                ))

        return alternatives

    async def rank_jobs(self, data: Dict[str, Any]) -> Dict[str, Job]:
        """
        Rank jobs by importance to customer.

        Args:
            data: Customer priority and purchase driver data

        Returns:
            Dictionary of ranked jobs by type

        TODO: For large datasets (>100 items), offload CPU-intensive keyword matching
        to asyncio.to_thread() to prevent blocking event loop.
        """
        self.logger.info("Ranking jobs by importance")

        priorities = data.get("customer_priorities", [])
        drivers = data.get("purchase_drivers", [])

        # Analyze priorities to determine importance
        social_importance = self._calculate_social_importance(priorities, drivers)
        emotional_importance = self._calculate_emotional_importance(priorities, drivers)
        functional_importance = self._calculate_functional_importance(priorities, drivers)

        ranked_jobs = {
            "functional": Job(
                job_type="functional",
                description="Accomplish practical task",
                importance=functional_importance
            ),
            "emotional": Job(
                job_type="emotional",
                description="Achieve desired emotional state",
                importance=emotional_importance
            ),
            "social": Job(
                job_type="social",
                description="Project desired social identity",
                importance=social_importance
            )
        }

        return ranked_jobs

    def _identify_functional_job(self, data: Dict[str, Any]) -> Job:
        """Identify the functional job (what product does)."""
        features = data.get("features", [])
        stated_benefits = data.get("stated_benefits", [])

        description = "Complete practical task efficiently"
        if features:
            description = f"Use {', '.join(features[:2])} to accomplish goals"

        return Job(
            job_type="functional",
            description=description,
            importance=0.6  # Functional is table stakes, not differentiator
        )

    def _identify_emotional_job(self, data: Dict[str, Any]) -> Job:
        """Identify the emotional job (how customer wants to feel)."""
        emotional_triggers = data.get("emotional_triggers", [])
        desired_outcomes = data.get("desired_outcomes", [])

        description = "Feel accomplished and in control"
        if emotional_triggers:
            description = f"Feel {', '.join(emotional_triggers[:2])}"
        elif desired_outcomes:
            description = f"Achieve {', '.join(desired_outcomes[:2])}"

        return Job(
            job_type="emotional",
            description=description,
            importance=0.75  # Often more important than functional
        )

    def _identify_social_job(self, data: Dict[str, Any]) -> Job:
        """Identify the social job (how customer wants to be perceived)."""
        usage_patterns = data.get("usage_patterns", [])

        # Social sharing indicates social job
        has_social_component = any(
            "social" in str(pattern).lower() or "share" in str(pattern).lower()
            for pattern in usage_patterns
        )

        description = "Be seen as successful and discerning"
        if has_social_component:
            description = "Signal status and belonging to desired group"

        importance = 0.8 if has_social_component else 0.5

        return Job(
            job_type="social",
            description=description,
            importance=importance
        )

    def _determine_primary_job(
        self,
        jobs: JobsAnalysis,
        ranked_jobs: Dict[str, Job]
    ) -> Job:
        """Determine which job is primary (usually emotional or social)."""
        # Create new Job instances with updated importance using Pydantic's copy method
        all_jobs = {}

        for job_type in ["functional", "emotional", "social"]:
            original_job = getattr(jobs, f"{job_type}_job")
            ranked_importance = ranked_jobs.get(job_type, original_job).importance

            # Use Pydantic's copy method to safely update importance
            all_jobs[job_type] = original_job.copy(update={"importance": ranked_importance})

        primary = max(all_jobs.values(), key=lambda j: j.importance)
        return primary

    def _calculate_social_importance(
        self,
        priorities: List[str],
        drivers: List[str]
    ) -> float:
        """Calculate importance of social job."""
        social_keywords = ["social", "status", "approval", "peer", "community", "belonging"]

        social_score = sum(
            1 for item in priorities + drivers
            if any(keyword in str(item).lower() for keyword in social_keywords)
        )

        total = len(priorities + drivers) or 1
        return min(social_score / total + 0.3, 1.0)  # Base of 0.3

    def _calculate_emotional_importance(
        self,
        priorities: List[str],
        drivers: List[str]
    ) -> float:
        """Calculate importance of emotional job."""
        emotional_keywords = ["feel", "emotion", "achievement", "motivation", "pride", "confidence"]

        emotional_score = sum(
            1 for item in priorities + drivers
            if any(keyword in str(item).lower() for keyword in emotional_keywords)
        )

        total = len(priorities + drivers) or 1
        return min(emotional_score / total + 0.4, 1.0)  # Base of 0.4

    def _calculate_functional_importance(
        self,
        priorities: List[str],
        drivers: List[str]
    ) -> float:
        """Calculate importance of functional job."""
        functional_keywords = ["utility", "practical", "functionality", "efficiency", "performance"]

        functional_score = sum(
            1 for item in priorities + drivers
            if any(keyword in str(item).lower() for keyword in functional_keywords)
        )

        total = len(priorities + drivers) or 1
        return min(functional_score / total + 0.3, 1.0)  # Base of 0.3
