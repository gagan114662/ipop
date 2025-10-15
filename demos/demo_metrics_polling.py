#!/usr/bin/env python3
"""
IPOP Hourly Metrics Polling Demo
===============================

This script demonstrates:
1. Real-time metrics polling from Meta and Google Ads
2. MongoDB updates every hour
3. Campaign performance tracking
4. Automated optimization decisions

Run this script to see the metrics polling system in action.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
import structlog

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import Database
from app.tasks.metrics_ingestion import MetricsIngestionService
from app.tasks.scheduler import AutomatedScheduler
from app.platforms.manager import PlatformManager
from app.models.campaign import Platform

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger(__name__)


class MetricsPollingDemo:
    """Demo class for metrics polling and optimization."""
    
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.db = None
        self.metrics_service = None
        self.scheduler = None
        
    async def setup_database(self):
        """Connect to MongoDB."""
        await Database.connect_db()
        self.db = Database.get_database()
        self.metrics_service = MetricsIngestionService(self.db)
        logger.info("database_connected")
    
    async def create_demo_campaigns(self):
        """Create demo campaigns for metrics polling."""
        demo_campaigns = [
            {
                "campaign_id": "DEMO_GA_001",
                "name": "Demo Google Ads Campaign",
                "platform": Platform.GOOGLE_ADS,
                "platform_campaign_id": "GA_123456789",
                "daily_budget": 100.0,
                "target_roas": 3.5,
                "status": "active",
                "client_id": "demo_client",
                "metadata": {
                    "customer_id": "123-456-7890",
                    "targeting": {
                        "geography": ["United States", "Canada"],
                        "keywords": ["digital marketing", "advertising"]
                    }
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "campaign_id": "DEMO_META_001",
                "name": "Demo Meta Campaign",
                "platform": Platform.META,
                "platform_campaign_id": "META_987654321",
                "daily_budget": 75.0,
                "target_roas": 4.0,
                "status": "active",
                "client_id": "demo_client",
                "metadata": {
                    "ad_account_id": "act_123456789",
                    "targeting": {
                        "geography": ["United States"],
                        "interests": ["fashion", "lifestyle"]
                    }
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        for campaign in demo_campaigns:
            await self.db.campaigns.insert_one(campaign)
            logger.info("demo_campaign_created", campaign_id=campaign["campaign_id"])
        
        return demo_campaigns
    
    async def simulate_platform_metrics(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate fetching metrics from platform APIs."""
        
        # Simulate realistic metrics based on campaign type and time
        base_metrics = {
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "spend": 0.0,
            "revenue": 0.0
        }
        
        # Add some randomness and time-based variation
        import random
        hour_factor = datetime.utcnow().hour / 24.0  # 0-1 based on hour of day
        
        if campaign["platform"] == Platform.GOOGLE_ADS:
            base_metrics.update({
                "impressions": int(15000 + random.randint(-3000, 5000) * hour_factor),
                "clicks": int(450 + random.randint(-100, 150) * hour_factor),
                "conversions": int(25 + random.randint(-5, 15) * hour_factor),
                "spend": round(125.50 + random.uniform(-25, 50) * hour_factor, 2),
                "revenue": round(400.00 + random.uniform(-50, 100) * hour_factor, 2)
            })
        elif campaign["platform"] == Platform.META:
            base_metrics.update({
                "impressions": int(12000 + random.randint(-2000, 4000) * hour_factor),
                "clicks": int(380 + random.randint(-80, 120) * hour_factor),
                "conversions": int(22 + random.randint(-4, 12) * hour_factor),
                "spend": round(95.75 + random.uniform(-20, 40) * hour_factor, 2),
                "revenue": round(350.00 + random.uniform(-40, 80) * hour_factor, 2)
            })
        
        # Calculate derived metrics
        if base_metrics["impressions"] > 0:
            base_metrics["ctr"] = round(base_metrics["clicks"] / base_metrics["impressions"], 4)
        else:
            base_metrics["ctr"] = 0.0
        
        if base_metrics["clicks"] > 0:
            base_metrics["cpc"] = round(base_metrics["spend"] / base_metrics["clicks"], 2)
        else:
            base_metrics["cpc"] = 0.0
        
        if base_metrics["conversions"] > 0:
            base_metrics["cpa"] = round(base_metrics["spend"] / base_metrics["conversions"], 2)
        else:
            base_metrics["cpa"] = 0.0
        
        if base_metrics["spend"] > 0:
            base_metrics["roas"] = round(base_metrics["revenue"] / base_metrics["spend"], 2)
        else:
            base_metrics["roas"] = 0.0
        
        # Add timestamp and metadata
        base_metrics.update({
            "timestamp": datetime.utcnow(),
            "campaign_id": campaign["campaign_id"],
            "platform": campaign["platform"].value,
            "platform_campaign_id": campaign["platform_campaign_id"],
            "client_id": campaign["client_id"]
        })
        
        return base_metrics
    
    async def poll_campaign_metrics(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Poll metrics for a single campaign."""
        try:
            logger.info("polling_campaign_metrics", campaign_id=campaign["campaign_id"])
            
            # Simulate platform API call
            metrics = await self.simulate_platform_metrics(campaign)
            
            # Store metrics in performance_metrics collection
            await self.db.performance_metrics.insert_one(metrics)
            
            # Update campaign current_metrics
            await self.db.campaigns.update_one(
                {"campaign_id": campaign["campaign_id"]},
                {
                    "$set": {
                        "current_metrics": {
                            "impressions": metrics["impressions"],
                            "clicks": metrics["clicks"],
                            "conversions": metrics["conversions"],
                            "spend": metrics["spend"],
                            "revenue": metrics["revenue"],
                            "ctr": metrics["ctr"],
                            "cpc": metrics["cpc"],
                            "cpa": metrics["cpa"],
                            "roas": metrics["roas"],
                            "last_updated": metrics["timestamp"]
                        },
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info("metrics_updated", campaign_id=campaign["campaign_id"], **metrics)
            return metrics
            
        except Exception as e:
            logger.error("metrics_polling_failed", campaign_id=campaign["campaign_id"], error=str(e))
            return None
    
    async def run_hourly_polling_cycle(self):
        """Run a complete hourly metrics polling cycle."""
        print(f"\n🔄 Running Hourly Metrics Polling Cycle")
        print(f"⏰ Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        # Get all active campaigns
        campaigns = await self.db.campaigns.find({"status": "active"}).to_list(length=None)
        
        if not campaigns:
            print("❌ No active campaigns found")
            return
        
        print(f"📊 Found {len(campaigns)} active campaigns")
        
        # Poll metrics for each campaign
        all_metrics = []
        for campaign in campaigns:
            metrics = await self.poll_campaign_metrics(campaign)
            if metrics:
                all_metrics.append(metrics)
                
                # Display metrics
                platform_emoji = "🔍" if campaign["platform"] == Platform.GOOGLE_ADS else "📱"
                print(f"\n{platform_emoji} {campaign['name']} ({campaign['platform'].value})")
                print(f"   Impressions: {metrics['impressions']:,}")
                print(f"   Clicks: {metrics['clicks']} (CTR: {metrics['ctr']:.2%})")
                print(f"   Conversions: {metrics['conversions']} (CPA: ${metrics['cpa']:.2f})")
                print(f"   Spend: ${metrics['spend']:.2f} (CPC: ${metrics['cpc']:.2f})")
                print(f"   Revenue: ${metrics['revenue']:.2f} (ROAS: {metrics['roas']:.2f})")
        
        # Calculate totals
        if all_metrics:
            total_impressions = sum(m["impressions"] for m in all_metrics)
            total_clicks = sum(m["clicks"] for m in all_metrics)
            total_conversions = sum(m["conversions"] for m in all_metrics)
            total_spend = sum(m["spend"] for m in all_metrics)
            total_revenue = sum(m["revenue"] for m in all_metrics)
            
            print(f"\n📈 Hourly Totals:")
            print(f"   Total Impressions: {total_impressions:,}")
            print(f"   Total Clicks: {total_clicks}")
            print(f"   Total Conversions: {total_conversions}")
            print(f"   Total Spend: ${total_spend:.2f}")
            print(f"   Total Revenue: ${total_revenue:.2f}")
            print(f"   Overall ROAS: {total_revenue/total_spend:.2f}" if total_spend > 0 else "   Overall ROAS: N/A")
        
        return all_metrics
    
    async def demonstrate_optimization_decisions(self, metrics: List[Dict[str, Any]]):
        """Demonstrate automated optimization decisions based on metrics."""
        print(f"\n🤖 Automated Optimization Decisions")
        print("-" * 40)
        
        for metric in metrics:
            campaign_id = metric["campaign_id"]
            roas = metric["roas"]
            target_roas = 3.5  # Default target
            
            # Get campaign details
            campaign = await self.db.campaigns.find_one({"campaign_id": campaign_id})
            if campaign:
                target_roas = campaign.get("target_roas", 3.5)
            
            # Make optimization decision
            if roas < target_roas * 0.8:  # 20% below target
                decision = "PAUSE_CAMPAIGN"
                action = "Pausing campaign due to poor ROAS performance"
            elif roas < target_roas * 0.9:  # 10% below target
                decision = "REDUCE_BUDGET"
                action = "Reducing budget by 20% due to below-target ROAS"
            elif roas > target_roas * 1.2:  # 20% above target
                decision = "INCREASE_BUDGET"
                action = "Increasing budget by 25% due to excellent ROAS"
            else:
                decision = "NO_ACTION"
                action = "Performance within acceptable range"
            
            print(f"🎯 {campaign_id}:")
            print(f"   Current ROAS: {roas:.2f} (Target: {target_roas:.2f})")
            print(f"   Decision: {decision}")
            print(f"   Action: {action}")
            
            # Store optimization decision
            decision_doc = {
                "campaign_id": campaign_id,
                "decision_type": decision,
                "action": action,
                "current_roas": roas,
                "target_roas": target_roas,
                "timestamp": datetime.utcnow(),
                "applied": False  # Would be True if actually applied
            }
            
            await self.db.optimization_decisions.insert_one(decision_doc)
    
    async def show_metrics_history(self, campaign_id: str, hours: int = 24):
        """Show metrics history for a campaign."""
        print(f"\n📊 Metrics History for {campaign_id} (Last {hours} hours)")
        print("-" * 50)
        
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        metrics_history = await self.db.performance_metrics.find({
            "campaign_id": campaign_id,
            "timestamp": {"$gte": start_time}
        }).sort("timestamp", 1).to_list(length=None)
        
        if not metrics_history:
            print("No metrics history found")
            return
        
        print(f"{'Time':<12} {'Impr':<8} {'Clicks':<6} {'Conv':<4} {'Spend':<8} {'ROAS':<6}")
        print("-" * 50)
        
        for metric in metrics_history:
            time_str = metric["timestamp"].strftime("%H:%M")
            print(f"{time_str:<12} {metric['impressions']:<8,} {metric['clicks']:<6} "
                  f"{metric['conversions']:<4} ${metric['spend']:<7.2f} {metric['roas']:<6.2f}")
    
    async def run_demo(self):
        """Run the complete metrics polling demo."""
        print("🚀 IPOP Hourly Metrics Polling Demo")
        print("=" * 50)
        
        # Setup
        await self.setup_database()
        
        # Create demo campaigns
        print("\n📝 Creating Demo Campaigns...")
        campaigns = await self.create_demo_campaigns()
        print(f"✅ Created {len(campaigns)} demo campaigns")
        
        # Run multiple polling cycles to show progression
        print(f"\n🔄 Running Multiple Polling Cycles...")
        
        for cycle in range(3):
            print(f"\n--- Cycle {cycle + 1} ---")
            metrics = await self.run_hourly_polling_cycle()
            
            if metrics:
                await self.demonstrate_optimization_decisions(metrics)
            
            # Wait a bit between cycles (in real system, this would be 1 hour)
            if cycle < 2:
                print(f"\n⏳ Waiting 5 seconds before next cycle...")
                await asyncio.sleep(5)
        
        # Show metrics history
        if campaigns:
            await self.show_metrics_history(campaigns[0]["campaign_id"], hours=3)
        
        print(f"\n🎉 Demo Complete!")
        print("=" * 50)
        print("Key Features Demonstrated:")
        print("✅ Hourly metrics polling from platforms")
        print("✅ Real-time MongoDB updates")
        print("✅ Automated optimization decisions")
        print("✅ Performance tracking and history")
        print("✅ Multi-platform campaign management")


async def main():
    """Main demo function."""
    demo = MetricsPollingDemo()
    
    try:
        await demo.run_demo()
        
    except Exception as e:
        logger.error("demo_failed", error=str(e))
        print(f"❌ Demo failed: {e}")
    
    finally:
        await Database.close_db()


if __name__ == "__main__":
    print("Starting IPOP Metrics Polling Demo...")
    print("This demo shows real-time metrics polling and optimization.")
    print()
    
    asyncio.run(main())
