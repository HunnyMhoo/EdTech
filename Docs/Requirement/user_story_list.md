# MVP User Stories – Thai Self-Learning App (GAT เชื่อมโยง)

## Batch 1: Core Learning Flow (Walking Skeleton)

### User Story 1.1: Launch Daily Mission
**User Story**: As a student, I want to start a daily mission with 5 questions, so that I can quickly begin learning without choosing topics manually.  
**Context**: Entry point into the app’s value; minimizes friction and ensures structured experience.  
**Priority**: Must Have  
**Acceptance Criteria**:
1. When I log in, I see a daily mission prompt.
2. The mission contains exactly 5 questions.
3. Questions are pulled from a predefined GAT เชื่อมโยง pool.  
**Dependencies**: Question pool must be loaded into backend or CMS.

### User Story 1.2: Complete Quiz with Instant Feedback
**User Story**: As a student, I want to answer a quiz and get immediate feedback, so that I understand my mistakes in real time.  
**Context**: Core to learning loop; the primary UX differentiator vs. books and videos.  
**Priority**: Must Have  
**Acceptance Criteria**:
1. I can select one answer from four choices.
2. After submission, I see the correct answer highlighted.
3. I see a short explanation (in Thai) of why my answer was correct or incorrect.  
**Dependencies**: Static feedback content for each question in database.

### User Story 1.3: Complete a Daily Mission
**User Story**: As a student, I want to complete all 5 questions in a mission, so that I feel a sense of accomplishment and progress.  
**Context**: End-to-end flow validation and minimum success metric for mission completion.  
**Priority**: Must Have  
**Acceptance Criteria**:
1. I can move sequentially through 5 questions.
2. After the final question, I see a mission complete screen.
3. My progress is saved to my user record.  
**Dependencies**: Completion logic and basic user session management.

## Batch 2: Adaptive Learning Logic

### User Story 2.1: Adjust Difficulty Based on Performance
**User Story**: As a student, I want future questions to get harder or easier depending on my previous answers, so that I stay challenged without getting frustrated.  
**Context**: Increases learning efficiency and personalization.  
**Priority**: Should Have  
**Acceptance Criteria**:
1. If I answer 2+ questions correctly, I get a more difficult question.
2. If I answer 2+ questions incorrectly, I get an easier question.
3. Difficulty levels are tagged in backend (easy/med/hard).  
**Dependencies**: Question metadata tagging; scoring logic; question selection algorithm.

### User Story 2.2: Reinforce Weak Concepts
**User Story**: As a student, I want to revisit topics I struggle with, so that I can improve specific skills over time.  
**Context**: Retention and concept mastery mechanism.  
**Priority**: Should Have  
**Acceptance Criteria**:
1. If I fail the same concept twice, it is automatically scheduled for future missions.
2. I can view a "Review" tag on weak questions in progress dashboard.  
**Dependencies**: Topic-tagged question bank; per-user history tracking.

## Batch 3: LINE OA Integration

### User Story 3.1: Receive Daily Reminder via LINE
**User Story**: As a student, I want to get a LINE message if I haven’t studied yet today, so that I stay consistent in my habits.  
**Context**: High-leverage retention strategy for Thai users.  
**Priority**: Must Have  
**Acceptance Criteria**:
1. If user has not started a mission by 7PM, a LINE message is sent.
2. The message contains a deep link to today’s mission.  
**Dependencies**: LINE OA integration; backend scheduler; user LINE ID linkage.

### User Story 3.2: Get Motivated on Mission Completion
**User Story**: As a student, I want a congratulatory LINE message when I finish a mission, so that I feel rewarded and return tomorrow.  
**Context**: Reinforces completion behavior and builds habit loop.  
**Priority**: Should Have  
**Acceptance Criteria**:
1. After finishing a mission, a LINE message is sent with streak update.  
**Dependencies**: Mission completion trigger; LINE webhook logic.

## Batch 4: Progress Tracking

### User Story 4.1: View My XP and Daily Streak
**User Story**: As a student, I want to see my XP and daily streak, so that I stay motivated to keep learning.  
**Context**: Core gamification mechanism for engagement.  
**Priority**: Must Have  
**Acceptance Criteria**:
1. I can view my XP total and streak count from the home or profile screen.
2. XP is awarded per question and mission.  
**Dependencies**: XP schema in backend; streak tracking logic.

### User Story 4.2: View Topic Mastery
**User Story**: As a student, I want to see my progress by topic, so that I know where I’ve improved and what to review.  
**Context**: Reinforces value of the adaptive system.  
**Priority**: Should Have  
**Acceptance Criteria**:
1. Each question is tagged with a concept (e.g., causal links).
2. I see a per-topic bar or percentage showing mastery.  
**Dependencies**: Question tagging; topic analytics.

## Batch 5: Content Management System (Internal Tool)

### User Story 5.1: Create and Tag Lessons
**User Story**: As a content editor, I want to create a lesson with a concept, example, and quiz, so that I can structure learning consistently.  
**Context**: Core to scaling and iterating content.  
**Priority**: Must Have  
**Acceptance Criteria**:
1. I can input a concept name, description, and example.
2. I can create 1 or more quiz questions per lesson.
3. Each question is tagged by difficulty and topic.  
**Dependencies**: CMS UI and backend APIs; question schema.

### User Story 5.2: Preview Student Experience
**User Story**: As an editor, I want to preview how a lesson or quiz looks in the app, so that I can confirm formatting and flow.  
**Context**: Prevents bad UX or broken inputs.  
**Priority**: Should Have  
**Acceptance Criteria**:
1. I can click “Preview” and see a mobile mockup.
2. Includes scroll and answer submission.  
**Dependencies**: CMS frontend; content rendering preview module.

## Batch 6: Optional AI Assist Module

### User Story 6.1: Auto-Generate Rationale
**User Story**: As a content creator, I want to generate Thai-language feedback for a quiz using AI, so that I can scale high-quality explanations.  
**Context**: Boosts efficiency and consistency in content generation.  
**Priority**: Nice to Have (Optional)  
**Acceptance Criteria**:
1. I click “Generate Explanation” in CMS.
2. AI returns a short Thai-language rationale for the correct answer.
3. I can edit the explanation before saving.  
**Dependencies**: OpenAI or local LLM API; CMS integration

## Delivery Plan – Iterative Milestones

Milestone 1: End-to-end mission with feedback (Weeks 1–2)  
- User Stories: 1.1, 1.2, 1.3

Milestone 2: LINE engagement and retention loop (Weeks 3–4)  
- User Stories: 3.1, 3.2, 4.1

Milestone 3: Adaptive and mastery tracking (Weeks 5–6)  
- User Stories: 2.1, 4.2

Milestone 4: CMS internal launch (Week 7)  
- User Stories: 5.1, 5.2

Milestone 5: AI Assist and polish (Week 8+)  
- User Story: 6.1
