from typing import List, Dict, Any, Optional

from backend.models.daily_mission import DailyMissionDocument, MissionStatus, Answer, AnswerAttempt
from backend.repositories.mission_repository import MissionRepository
from backend.services.utils import (
    get_utc7_today_date,
    get_current_time_in_target_timezone,
)

def _is_answer_correct(user_answer: str, correct_answer_id: str) -> bool:
    """
    Determines if the user's answer is correct.
    
    Args:
        user_answer: The user's submitted answer
        correct_answer_id: The correct answer ID from the question
    
    Returns:
        True if the answer is correct, False otherwise
    """
    return str(user_answer).strip().lower() == str(correct_answer_id).strip().lower()

def _is_mission_complete(mission: DailyMissionDocument) -> bool:
    """
    Checks if a mission is complete.

    A mission is considered complete if all questions have been completed
    (either answered correctly or maximum retries reached) and feedback has been shown.

    Args:
        mission: The daily mission document.

    Returns:
        True if the mission is complete, False otherwise.
    """
    # Condition 1: The number of answers must equal the number of questions.
    if len(mission.answers) != len(mission.questions):
        return False

    # Condition 2: Every answer must be marked as complete and feedback shown.
    return all(answer.is_complete and answer.feedback_shown for answer in mission.answers)

def _find_or_create_answer(answers: List[Answer], question_id: str) -> Answer:
    """
    Finds existing answer or creates a new one for the given question.
    
    Args:
        answers: List of existing answers
        question_id: The question ID to find/create answer for
    
    Returns:
        The existing or newly created Answer object
    """
    for answer in answers:
        if answer.question_id == question_id:
            return answer
    
    # Create new answer if not found
    new_answer = Answer(question_id=question_id, current_answer="")
    answers.append(new_answer)
    return new_answer

async def submit_answer_with_feedback(
    user_id: str,
    question_id: str,
    user_answer: Any,
    mission_repo: MissionRepository,
) -> Dict[str, Any]:
    """
    Submits an answer and returns feedback information.
    
    Args:
        user_id: The user ID
        question_id: The question ID being answered
        user_answer: The user's answer
        mission_repo: The mission repository
    
    Returns:
        Dictionary containing feedback information
    """
    today_target_tz_date = get_utc7_today_date()
    mission_doc = await mission_repo.find_mission(user_id, today_target_tz_date)

    if not mission_doc:
        raise ValueError("No active mission found for user")

    # Find the question
    question = None
    for q in mission_doc.questions:
        if q.question_id == question_id:
            question = q
            break
    
    if not question:
        raise ValueError(f"Question {question_id} not found in mission")

    # Find or create answer
    answer = _find_or_create_answer(mission_doc.answers, question_id)
    
    # Check if already completed
    if answer.is_complete:
        return {
            "already_complete": True,
            "is_correct": answer.is_correct,
            "correct_answer": question.correct_answer_id,
            "explanation": question.feedback_th,
            "attempt_count": answer.attempt_count
        }
    
    # Check correctness
    is_correct = _is_answer_correct(user_answer, question.correct_answer_id)
    
    # Update answer
    answer.current_answer = user_answer
    answer.is_correct = is_correct
    answer.attempt_count += 1
    
    # Add to attempts history
    attempt = AnswerAttempt(answer=user_answer, is_correct=is_correct)
    answer.attempts_history.append(attempt)
    
    # Mark as complete if correct or max retries reached
    if is_correct or answer.attempt_count >= answer.max_retries:
        answer.is_complete = True
    
    # Update mission status
    if _is_mission_complete(mission_doc):
        mission_doc.status = MissionStatus.COMPLETE
    else:
        mission_doc.status = MissionStatus.IN_PROGRESS
    
    mission_doc.updated_at = get_current_time_in_target_timezone()
    await mission_repo.save_mission(mission_doc)
    
    return {
        "already_complete": False,
        "is_correct": is_correct,
        "correct_answer": question.correct_answer_id,
        "explanation": question.feedback_th,
        "attempt_count": answer.attempt_count,
        "max_retries": answer.max_retries,
        "can_retry": not answer.is_complete,
        "question_complete": answer.is_complete
    }

async def mark_feedback_shown(
    user_id: str,
    question_id: str,
    mission_repo: MissionRepository,
) -> Optional[DailyMissionDocument]:
    """
    Marks feedback as shown for a specific question.
    
    Args:
        user_id: The user ID
        question_id: The question ID
        mission_repo: The mission repository
    
    Returns:
        Updated mission document or None if not found
    """
    today_target_tz_date = get_utc7_today_date()
    mission_doc = await mission_repo.find_mission(user_id, today_target_tz_date)

    if not mission_doc:
        return None

    # Find the answer and mark feedback as shown
    for answer in mission_doc.answers:
        if answer.question_id == question_id:
            answer.feedback_shown = True
            break
    
    # Update mission status
    if _is_mission_complete(mission_doc):
        mission_doc.status = MissionStatus.COMPLETE
    
    mission_doc.updated_at = get_current_time_in_target_timezone()
    await mission_repo.save_mission(mission_doc)
    
    return mission_doc

async def reset_question_for_retry(
    user_id: str,
    question_id: str,
    mission_repo: MissionRepository,
) -> Dict[str, Any]:
    """
    Resets a question for retry (clears current answer but keeps history).
    
    Args:
        user_id: The user ID
        question_id: The question ID to reset
        mission_repo: The mission repository
    
    Returns:
        Dictionary with reset status
    """
    today_target_tz_date = get_utc7_today_date()
    mission_doc = await mission_repo.find_mission(user_id, today_target_tz_date)

    if not mission_doc:
        return {"success": False, "error": "No active mission found"}

    # Find the answer
    answer = None
    for ans in mission_doc.answers:
        if ans.question_id == question_id:
            answer = ans
            break
    
    if not answer:
        return {"success": False, "error": "Answer not found"}
    
    if answer.is_complete:
        return {"success": False, "error": "Question already completed"}
    
    if answer.attempt_count >= answer.max_retries:
        return {"success": False, "error": "Maximum retries exceeded"}
    
    # Reset current answer but keep history and attempt count
    answer.current_answer = ""
    answer.feedback_shown = False
    
    mission_doc.updated_at = get_current_time_in_target_timezone()
    await mission_repo.save_mission(mission_doc)
    
    return {
        "success": True,
        "remaining_attempts": answer.max_retries - answer.attempt_count
    }

async def update_mission_progress(
    user_id: str,
    current_question_index: int,
    answers: List[Dict[str, Any]],
    mission_repo: MissionRepository,
) -> Optional[DailyMissionDocument]:
    """
    Updates the progress of today's mission for a given user.
    This function is maintained for backward compatibility.
    """
    today_target_tz_date = get_utc7_today_date()
    mission_doc = await mission_repo.find_mission(user_id, today_target_tz_date)

    if not mission_doc:
        return None

    mission_doc.current_question_index = current_question_index
    
    # Convert old format answers to new Answer model if needed
    new_answers = []
    for ans_dict in answers:
        if isinstance(ans_dict, dict):
            answer = Answer(
                question_id=ans_dict["question_id"],
                current_answer=ans_dict.get("answer", ""),
                feedback_shown=ans_dict.get("feedback_shown", False),
                is_complete=ans_dict.get("is_complete", False),
                is_correct=ans_dict.get("is_correct", False),
                attempt_count=ans_dict.get("attempt_count", 1)
            )
            new_answers.append(answer)
    
    mission_doc.answers = new_answers
    
    # Automatically update the status to COMPLETED if all conditions are met
    if _is_mission_complete(mission_doc):
        mission_doc.status = MissionStatus.COMPLETE
    else:
        mission_doc.status = MissionStatus.IN_PROGRESS
        
    mission_doc.updated_at = get_current_time_in_target_timezone()

    await mission_repo.save_mission(mission_doc)
    return mission_doc 