# Implementation Plan: Launch Daily Mission Feature

## Assumptions

- Frontend: React Native (no extra framework; functional components with hooks)
- Backend: Python with FastAPI
- Database: MongoDB (using Mongoose)
- Auth: LINE Login (planned but not implemented in this task)
- Timezone for mission reset: UTC+7
- Daily mission is stored per user in DB with status tracking
- Focus is on modularity, testability, and clean architecture

---

## Task 1: Define Daily Mission Data Schema

* Task Description: Create a MongoDB schema for storing each user's daily mission, including questions and completion status.
* Location: backend/models/daily_mission.py
* Implementation Notes:
  - Schema fields: userId, date, questionIds[], status (not_started, in_progress, complete), createdAt
  - Index userId + date to prevent duplicates
* Automated Tests:
  - Unit test for schema validation and default fields (Jest + in-memory MongoDB)
* Manual Verification:
  - Use MongoDB Compass to verify data is inserted correctly
* Best Practices to Follow:
  - Use snake_case for DB fields, camelCase in code
  - Validate input with Mongoose schema types

---

## Task 2: Create Daily Mission Generation Service

* Task Description: Implement logic to generate and persist a new daily mission with 5 questions per user per day.
* Location: backend/services/mission_service.py
* Implementation Notes:
  - Select 5 random questionIds from the GAT pool
  - Check if today's mission already exists before inserting
  - Timezone-aware date handling (use moment-timezone or native Date with offset)
* Automated Tests:
  - Unit test for mission creation with mock question pool
  - Edge case: duplicate prevention, empty pool
* Manual Verification:
  - Call endpoint with httpie or curl to simulate daily login
* Best Practices to Follow:
  - Wrap random logic in utility function
  - Avoid hardcoded pool IDs

---

## Task 3: Create Mission Retrieval API Endpoint

* Task Description: Build an API endpoint to fetch today's mission for the logged-in user.
* Location: backend/routes/missions.py
* Implementation Notes:
  - Route: GET /api/missions/today
  - Middleware: simulate user context via hardcoded token or test user
* Automated Tests:
  - Integration test for GET /api/missions/today with mock DB
* Manual Verification:
  - Open app -> fetch mission -> check it loads correctly
* Best Practices to Follow:
  - Use async/await + try/catch
  - Return structured JSON (status, data, message)

---

## Task 4: Integrate Mission API into React Native App

* Task Description: Fetch mission data on app load and display to student.
* Location: frontend/screens/HomeScreen.tsx
* Implementation Notes:
  - Use useEffect to call API
  - Use TailwindCSS utility classes for layout and spacing (via tailwind-rn or twin.macro)
  - Store mission in local state (or context if already available)
* Automated Tests:
  - Unit test API call function (Jest with fetch mock)
* Manual Verification:
  - Launch app as a test user and confirm 5-question mission loads
* Best Practices to Follow:
  - Modularize API calls in services/missionApi.ts
  - Add basic error handling (e.g., toast on failure)

---

## Task 5: Handle Mission Resume on Reopen

* Task Description: Resume mission if already in progress
* Location: frontend/screens/MissionScreen.tsx
* Implementation Notes:
  - Store current question index in state
  - Resume from last answered or allow re-review
* Automated Tests:
  - Unit test for question index tracking and navigation
* Manual Verification:
  - Start a mission -> kill app -> reopen and continue
* Best Practices to Follow:
  - Persist current progress in localStorage or backend

---

## Task 6: Implement Daily Reset Backend Job

* Task Description: Implement a cron job to reset missions daily per user. This job archives incomplete missions from previous days (UTC+7).
* Location: `backend/jobs/daily_reset.py` (job logic), `backend/main.py` (scheduler integration), `backend/services/mission_service.py` (archiving logic), `backend/models/daily_mission.py` (status update).
* Implementation Notes:
  - Job scheduled via APScheduler in `backend/main.py` to run at 4AM UTC daily.
  - Old, incomplete missions are marked with status `ARCHIVED`.
  - Service function `archive_past_incomplete_missions` in `mission_service.py` handles the logic.
  - `MissionStatus` enum in `daily_mission.py` updated with `ARCHIVED` status.
* Automated Tests:
  - Unit tests for `ARCHIVED` status in `DailyMissionDocument` model.
  - Unit tests for `archive_past_incomplete_missions` service function (mocking DB).
  - Unit tests for `run_daily_reset_job` job function (mocking service calls and checking logs).
* Manual Verification:
  - Trigger job manually (e.g., by adjusting schedule or running `daily_reset.py` script) and inspect mock DB state and application logs.
* Best Practices to Follow:
  - In-app scheduler (APScheduler) for job management integrated with the application lifecycle.
  - Clear logging for job execution and scheduler events.
  - Soft-delete (archiving) strategy to preserve data.
  - Timezone consistency (UTC for scheduler, UTC+7 for mission logic).
  - Comprehensive unit testing for new logic.

---
