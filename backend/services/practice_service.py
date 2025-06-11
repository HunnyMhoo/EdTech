from datetime import datetime
from typing import List, Optional, Dict, Any
import random

from backend.models.practice_session import PracticeSession, PracticeAnswer, PracticeSessionStatus
from backend.models.daily_mission import Question
from backend.repositories.practice_repository import PracticeRepository
from backend.repositories.question_repository import QuestionRepository

# Custom Exceptions
class PracticeServiceError(Exception):
    """Base exception for practice service issues."""
    pass

class InsufficientQuestionsError(PracticeServiceError):
    """Raised when there aren't enough questions for the requested topic and count."""
    pass

class SessionNotFoundError(PracticeServiceError):
    """Raised when a practice session is not found."""
    pass

class SessionAlreadyCompletedError(PracticeServiceError):
    """Raised when trying to modify a completed session."""
    pass

async def create_practice_session(
    user_id: str,
    topic: str,
    question_count: int,
    question_repo: QuestionRepository,
    practice_repo: PracticeRepository
) -> PracticeSession:
    """
    Creates a new practice session with questions from the specified topic.
    
    Args:
        user_id: The user ID
        topic: The topic/skill_area to practice
        question_count: Number of questions to include
        question_repo: Question repository
        practice_repo: Practice repository
    
    Returns:
        Created practice session
        
    Raises:
        InsufficientQuestionsError: If not enough questions available for the topic
    """
    # Validate question count
    if question_count < 1 or question_count > 20:
        raise PracticeServiceError("Question count must be between 1 and 20")
    
    # Check if topic has enough questions
    topic_question_count = await question_repo.get_topic_question_count(topic)
    if topic_question_count < question_count:
        raise InsufficientQuestionsError(
            f"Topic '{topic}' only has {topic_question_count} questions, "
            f"but {question_count} were requested"
        )
    
    # Get random questions for the topic
    questions = await question_repo.get_questions_by_topic(topic, question_count)
    
    if len(questions) < question_count:
        raise InsufficientQuestionsError(
            f"Could not retrieve {question_count} questions for topic '{topic}'"
        )
    
    # Create practice session
    practice_session = PracticeSession(
        user_id=user_id,
        topic=topic,
        question_count=question_count,
        questions=questions
    )
    
    # Save to database
    await practice_repo.create_session(practice_session)
    
    return practice_session

async def get_practice_session(
    session_id: str,
    practice_repo: PracticeRepository
) -> PracticeSession:
    """
    Retrieves a practice session by ID.
    
    Args:
        session_id: The session ID
        practice_repo: Practice repository
    
    Returns:
        Practice session
        
    Raises:
        SessionNotFoundError: If session is not found
    """
    session = await practice_repo.find_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Practice session '{session_id}' not found")
    
    return session

async def submit_practice_answer(
    session_id: str,
    question_id: str,
    user_answer: Any,
    practice_repo: PracticeRepository
) -> Dict[str, Any]:
    """
    Submits an answer for a practice question and returns feedback.
    
    Args:
        session_id: The session ID
        question_id: The question ID
        user_answer: The user's answer
        practice_repo: Practice repository
    
    Returns:
        Dictionary containing feedback information
        
    Raises:
        SessionNotFoundError: If session is not found
        SessionAlreadyCompletedError: If session is already completed
        PracticeServiceError: If question is not found in session
    """
    # Get session
    session = await practice_repo.find_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Practice session '{session_id}' not found")
    
    if session.status == PracticeSessionStatus.COMPLETED:
        raise SessionAlreadyCompletedError("Cannot submit answer to completed session")
    
    # Find the question
    question = None
    for q in session.questions:
        if q.question_id == question_id:
            question = q
            break
    
    if not question:
        raise PracticeServiceError(f"Question '{question_id}' not found in session")
    
    # Check if already answered
    existing_answer = None
    for answer in session.answers:
        if answer.question_id == question_id:
            existing_answer = answer
            break
    
    if existing_answer:
        # Return existing feedback
        return {
            "already_answered": True,
            "is_correct": existing_answer.is_correct,
            "correct_answer": question.correct_answer_id,
            "explanation": question.feedback_th,
            "user_answer": existing_answer.user_answer
        }
    
    # Check answer correctness
    is_correct = _is_answer_correct(user_answer, question.correct_answer_id)
    
    # Create answer record
    practice_answer = PracticeAnswer(
        question_id=question_id,
        user_answer=user_answer,
        is_correct=is_correct
    )
    
    # Add answer to session
    session.answers.append(practice_answer)
    
    # Check if session is complete
    if session.is_complete():
        session.mark_completed()
    
    # Update session in database
    await practice_repo.update_session(session)
    
    return {
        "already_answered": False,
        "is_correct": is_correct,
        "correct_answer": question.correct_answer_id,
        "explanation": question.feedback_th,
        "user_answer": user_answer,
        "session_complete": session.status == PracticeSessionStatus.COMPLETED,
        "progress": {
            "answered": len(session.answers),
            "total": len(session.questions)
        }
    }

async def get_practice_session_summary(
    session_id: str,
    practice_repo: PracticeRepository
) -> Dict[str, Any]:
    """
    Gets summary statistics for a practice session.
    
    Args:
        session_id: The session ID
        practice_repo: Practice repository
    
    Returns:
        Dictionary containing session summary
        
    Raises:
        SessionNotFoundError: If session is not found
    """
    session = await practice_repo.find_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Practice session '{session_id}' not found")
    
    score = session.calculate_score()
    
    return {
        "session_id": session.session_id,
        "topic": session.topic,
        "status": session.status,
        "created_at": session.created_at,
        "completed_at": session.completed_at,
        "score": score,
        "questions_answered": len(session.answers),
        "total_questions": len(session.questions),
        "correct_answers": session.correct_count if session.status == PracticeSessionStatus.COMPLETED else score["correct_answers"]
    }

async def get_available_practice_topics(
    question_repo: QuestionRepository
) -> List[Dict[str, Any]]:
    """
    Gets all available topics for practice with question counts.
    
    Args:
        question_repo: Question repository
    
    Returns:
        List of topic information dictionaries
    """
    topics = await question_repo.get_available_topics()
    
    topic_info = []
    for topic in topics:
        question_count = await question_repo.get_topic_question_count(topic)
        topic_info.append({
            "name": topic,
            "question_count": question_count,
            "available": question_count > 0
        })
    
    return topic_info

def _is_answer_correct(user_answer: Any, correct_answer: str) -> bool:
    """
    Checks if the user's answer matches the correct answer.
    Handles string comparison with case insensitivity and whitespace trimming.
    """
    if user_answer is None or correct_answer is None:
        return False
    
    # Convert to strings and normalize
    user_str = str(user_answer).strip().lower()
    correct_str = str(correct_answer).strip().lower()
    
    return user_str == correct_str 