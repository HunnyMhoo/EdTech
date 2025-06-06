import asyncio
import logging
from datetime import datetime, timezone

from backend.services.mission_service import archive_past_incomplete_missions, MissionGenerationError

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def run_daily_reset_job():
    """
    Job to be scheduled daily.
    This job archives incomplete missions from previous days.
    """
    logger.info("Starting daily reset job...")
    try:
        archived_count = await archive_past_incomplete_missions()
        logger.info(f"Daily reset job completed. Archived {archived_count} missions.")
    except MissionGenerationError as e: # Catching specific errors from service if any are relevant
        logger.error(f"Error during daily reset job (MissionGenerationError): {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during daily reset job: {e}", exc_info=True)

if __name__ == '__main__':
    # This allows running the job manually for testing
    logger.info("Running daily_reset.py manually for testing.")
    asyncio.run(run_daily_reset_job()) 