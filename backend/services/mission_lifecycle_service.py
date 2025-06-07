import asyncio

from backend.models.daily_mission import MissionStatus
from backend.repositories.mission_repository import MissionRepository
from backend.services.utils import (
    get_utc7_today_date,
    get_current_time_in_target_timezone,
)

async def archive_past_incomplete_missions(mission_repo: MissionRepository) -> int:
    """
    Archives missions from previous days (UTC+7) that are not yet complete or already archived.
    Returns the count of archived missions.
    """
    archived_count = 0
    today_utc7 = get_utc7_today_date()
    
    missions_to_update = await mission_repo.get_missions_to_archive(today_utc7)
    
    if not missions_to_update:
        return 0

    update_tasks = []
    for mission_doc in missions_to_update:
        mission_doc.status = MissionStatus.ARCHIVED
        mission_doc.updated_at = get_current_time_in_target_timezone()
        update_tasks.append(mission_repo.save_mission(mission_doc))
    
    await asyncio.gather(*update_tasks)
    
    archived_count = len(missions_to_update)
    return archived_count 