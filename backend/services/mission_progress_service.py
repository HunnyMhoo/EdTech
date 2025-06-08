from typing import List, Dict, Any, Optional

from backend.models.daily_mission import DailyMissionDocument, MissionStatus
from backend.repositories.mission_repository import MissionRepository
from backend.services.utils import (
    get_utc7_today_date,
    get_current_time_in_target_timezone,
)

def _is_mission_complete(mission: DailyMissionDocument) -> bool:
    """
    Checks if a mission is complete.

    A mission is considered complete if all questions have been answered
    and the user has viewed the feedback for every answer.

    Args:
        mission: The daily mission document.

    Returns:
        True if the mission is complete, False otherwise.
    """
    # Condition 1: The number of answers must equal the number of questions.
    if len(mission.answers) != len(mission.questions):
        return False

    # Condition 2: Every answer must have the 'feedback_shown' flag set to True.
    # This ensures the user has seen the outcome of their answer.
    return all(answer.get("feedback_shown", False) for answer in mission.answers)

async def update_mission_progress(
    user_id: str,
    current_question_index: int,
    answers: List[Dict[str, Any]],
    mission_repo: MissionRepository,
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
    
    # Automatically update the status to COMPLETED if all conditions are met
    if _is_mission_complete(mission_doc):
        mission_doc.status = MissionStatus.COMPLETE
    else:
        # If not yet complete, ensure the status reflects that it's in progress
        mission_doc.status = MissionStatus.IN_PROGRESS
        
    mission_doc.updated_at = get_current_time_in_target_timezone()

    await mission_repo.save_mission(mission_doc)
    return mission_doc 