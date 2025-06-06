1. Extend Question Data Model with Feedback
Task Description: Add a feedback_th field to each question in the source dataset (CSV).

Location: backend/data/gat_questions.csv

Implementation Notes:

Format: Add a column feedback_th containing short Thai explanations.

Ensure data is quoted properly for commas and newline safety.

Automated Tests:

N/A (CSV format change).

Manual Verification:

Open the CSV and confirm rows show correct Thai feedback.

Best Practices:

Use UTF-8 encoding.

Keep explanations concise (1–2 lines).

2. Update Question Loading Logic to Include Feedback
Task Description: Modify backend logic that loads questions to parse feedback_th.

Location: backend/services/mission_service.py

Implementation Notes:

Update CSV parsing to extract and attach feedback_th to each question.

You may define a QuestionData Pydantic model.

Automated Tests:

Add unit tests for _load_questions_from_csv covering feedback parsing and fallback behavior.

Manual Verification:

Add a debug route or log to print loaded question objects with feedback.

Best Practices:

Log missing or malformed feedback, but don’t fail mission generation.

3. Add New API to Fetch Question Metadata (Optional Suggestion)
Task Description: Create GET /questions/{id} to fetch full question + choices + feedback by ID.

Location: backend/routes/questions.py

Implementation Notes:

Keeps /missions/today lightweight (returns only question_ids).

Enables lazy loading of details per question.

Automated Tests:

Use FastAPI TestClient to validate correct question is returned.

Cover 404 for unknown ID, malformed input, etc.

Manual Verification:

Call endpoint with a real question ID and validate output.

Best Practices:

Standardize response format using MissionResponse[Question].

Sanitize and validate question ID input.

4. Enhance Frontend to Display Choices and Submit Answers
Task Description: Modify MissionScreen.tsx to show multiple-choice options.

Location: frontend/screens/MissionScreen.tsx

Implementation Notes:

Render choices as selectable radio buttons or styled buttons.

Use component state to track selected choice.

Automated Tests:

Use Jest + React Native Testing Library to test rendering and selection logic.

Manual Verification:

Run app → open mission → answer a question.

Best Practices:

Use question_id as key.

Ensure accessibility (aria where relevant).

5. Show Instant Feedback via Modal/Snackbar
Task Description: Show feedback when the student submits an answer.

Location: frontend/screens/MissionScreen.tsx

Implementation Notes:

Use a modal/snackbar to show:

“Correct!” or “Incorrect”

The correct answer

Thai explanation (feedback_th)

Dismiss modal to retry or go next.

Automated Tests:

Mock submission + test modal content based on correctness.

Manual Verification:

Answer a question and confirm visual feedback works.

Best Practices:

Use Alert, Modal, or 3rd-party UI lib if available (e.g., react-native-toast-message).

Avoid blocking UI unnecessarily — feedback should feel light and fast.

6. Persist Progress via Backend
Task Description: After feedback is shown, update backend with answer + mark feedback viewed.

Location:

Backend: backend/routes/missions.py, mission_service.py

Frontend: frontend/services/missionApi.ts

Implementation Notes:

Update answers[] with:

json
Copy
Edit
{ "question_id": "q1", "answer": "A", "feedback_shown": true }
Extend MissionProgressUpdatePayload accordingly.

Automated Tests:

Backend: Add tests for correct parsing and persistence of the new feedback_shown flag.

Frontend: Unit test API calls and payload formation.

Manual Verification:

Check backend logs to confirm payload received and stored.

Best Practices:

Defensive coding: ignore duplicate submits, idempotent updates.

7. Mark Mission Complete Only After All Feedback Seen
Task Description: Automatically mark mission as complete if all questions answered and feedback_shown = true.

Location: mission_service.py → update_mission_progress

Implementation Notes:

Add check: if all questions have valid answers + feedback_shown = true → mark status = complete.

Automated Tests:

Unit test with partial and full mission progress states.

Manual Verification:

Complete a mission and confirm status update via /missions/today.

Best Practices:

Use utility function is_mission_complete(mission) to isolate logic.

