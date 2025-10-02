#!/usr/bin/env python3
import asyncio
import logging
import signal
import sys
from app.workers.resize_worker import start_worker, stop_worker, worker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the worker with graceful shutdown"""
    
    # Handle shutdown signals
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(stop_worker())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("Starting resize worker...")
        await start_worker()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Worker failed: {e}", exc_info=True)
    finally:
        logger.info("Worker shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
