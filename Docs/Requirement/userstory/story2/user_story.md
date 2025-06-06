User Story 1.2: Complete Quiz with Instant Feedback
User Story
As a student, I want to answer a multiple-choice quiz and receive immediate feedback, so that I can understand my mistakes and improve my learning in real time.

Context
This feature is central to the platform’s interactive learning experience and is a key UX differentiator versus traditional media like books or static video. It leverages the system’s mission tracking, question bank, and real-time API architecture.

Priority
Must Have

Scope

One question is shown at a time from the daily mission.

Users can select one answer from multiple choices.

Feedback is displayed immediately upon submission.

Feedback content is pre-authored and stored in the backend database or CSV pool.

Acceptance Criteria

I can view one question at a time from the current daily mission.

I can select a single answer from four multiple-choice options.

After submitting my answer:

The correct answer is visually highlighted.

I receive an explanation in Thai about why my answer is correct or incorrect.

My answer is saved as part of the mission progress via the /api/missions/today/progress endpoint.

The UI updates the current question index and allows me to proceed to the next question.

Technical Considerations

Answers and explanations are tied to question_id and managed via the answers field in DailyMissionDocument.

Feedback content should be included in the question source (e.g., gat_questions.csv) or extended schema.

Frontend should persist state and update via updateMissionProgressApi.

Dependencies

Static feedback content must be defined for each question in the backend dataset (currently CSV-based or database).

Functional PUT /missions/today/progress API and working mission state management in MissionScreen.tsx.

