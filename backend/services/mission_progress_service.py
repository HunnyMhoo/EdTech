from typing import List, Dict, Any, Optional

from backend.models.daily_mission import DailyMissionDocument, MissionStatus
from backend.repositories.mission_repository import MissionRepository
from backend.services.utils import (
    get_utc7_today_date,
    get_current_time_in_target_timezone,
)

async def update_mission_progress(
    user_id: str,
    current_question_index: int,
    answers: List[Dict[str, Any]],
    mission_repo: MissionRepository,
    status: Optional[MissionStatus] = None
) -> Optional[DailyMissionDocument]:
    """
    Updates the progress of today's mission for a given user.
    """
    today_target_tz_date = get_utc7_today_date()
    mission_doc = await mission_repo.find_mission(user_id, today_target_tz_date)

    if not mission_doc:
        return None

    mission_doc.current_question_index = current_question_index
    mission_doc.answers = answers
    if status:
        mission_doc.status = status
    mission_doc.updated_at = get_current_time_in_target_timezone()

    await mission_repo.save_mission(mission_doc)
    return mission_doc 