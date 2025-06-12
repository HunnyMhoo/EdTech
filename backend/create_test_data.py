#!/usr/bin/env python3
"""
Script to create test data for Review Mistakes feature
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from database import db_manager
from models.daily_mission import DailyMissionDocument, MissionStatus, Question, Answer, ChoiceOption

async def create_test_data():
    """Create test missions with incorrect answers for Review Mistakes testing"""
    db = db_manager.get_database()
    missions_collection = db['daily_missions']
    
    # Create test questions
    question1 = Question(
        question_id='test_q1',
        question_text='What is 2 + 2?',
        skill_area='Mathematics',
        difficulty_level=1,
        choices=[
            ChoiceOption(id='a', text='3'),
            ChoiceOption(id='b', text='4'), 
            ChoiceOption(id='c', text='5')
        ],
        correct_answer_id='b',
        feedback_th='2 + 2 = 4 เป็นการบวกพื้นฐาน'
    )
    
    question2 = Question(
        question_id='test_q2', 
        question_text='What is 5 - 3?',
        skill_area='Mathematics',
        difficulty_level=1,
        choices=[
            ChoiceOption(id='a', text='1'),
            ChoiceOption(id='b', text='2'),
            ChoiceOption(id='c', text='3')
        ],
        correct_answer_id='b',
        feedback_th='5 - 3 = 2 เป็นการลบพื้นฐาน'
    )
    
    question3 = Question(
        question_id='test_q3',
        question_text='What is the capital of Thailand?',
        skill_area='Geography', 
        difficulty_level=2,
        choices=[
            ChoiceOption(id='a', text='Bangkok'),
            ChoiceOption(id='b', text='Chiang Mai'),
            ChoiceOption(id='c', text='Phuket')
        ],
        correct_answer_id='a',
        feedback_th='กรุงเทพฯ เป็นเมืองหลวงของประเทศไทย'
    )
    
    # Create test answers (incorrect)
    answer1 = Answer(
        question_id='test_q1',
        current_answer='a',  # Wrong answer (3 instead of 4)
        is_correct=False,
        attempt_count=2,
        is_complete=True,
        feedback_shown=True
    )
    
    answer2 = Answer(
        question_id='test_q2', 
        current_answer='c',  # Wrong answer (3 instead of 2)
        is_correct=False,
        attempt_count=1,
        is_complete=True,
        feedback_shown=True
    )
    
    answer3 = Answer(
        question_id='test_q3',
        current_answer='b',  # Wrong answer (Chiang Mai instead of Bangkok)
        is_correct=False,
        attempt_count=3,
        is_complete=True,
        feedback_shown=True
    )
    
    # Create test missions for different dates
    yesterday = datetime.now().date() - timedelta(days=1)
    two_days_ago = datetime.now().date() - timedelta(days=2)
    
    # Mission 1: Yesterday with 2 math mistakes
    test_mission1 = DailyMissionDocument(
        user_id='test_user_123',  # Default test user
        date=yesterday,
        questions=[question1, question2],
        answers=[answer1, answer2],
        status=MissionStatus.COMPLETE,
        current_question_index=2
    )
    
    # Mission 2: Two days ago with 1 geography mistake  
    test_mission2 = DailyMissionDocument(
        user_id='test_user_123',
        date=two_days_ago,
        questions=[question3],
        answers=[answer3], 
        status=MissionStatus.COMPLETE,
        current_question_index=1
    )
    
    # Clear existing test data
    await missions_collection.delete_many({"user_id": "test_user_123"})
    
    # Insert test missions
    await missions_collection.insert_one(test_mission1.model_dump())
    await missions_collection.insert_one(test_mission2.model_dump())
    
    print('✅ Test data created successfully!')
    print(f'Created missions for user: test_user_123')
    print(f'Mission 1 date: {yesterday} (2 Mathematics mistakes)')
    print(f'Mission 2 date: {two_days_ago} (1 Geography mistake)')
    print(f'Total mistakes: 3')
    print('\nNow you can test:')
    print('- All Mistakes tab: Should show 3 mistakes')
    print('- By Date tab: Should group by 2 different dates')
    print('- By Topic tab: Should group Mathematics vs Geography')

if __name__ == "__main__":
    asyncio.run(create_test_data()) 