# Implementation Strategy

This document outlines the strategy for implementing the EdTech Platform, focusing on the initial Daily Mission feature. It is based on the detailed [User Story 1 Implementation Plan](Requirement/userstory/story1/implementation_plan.md).

## Build Phases & Rationale

The implementation is broken down into distinct tasks, treated as mini-phases, to ensure a modular and testable build process. Each task focuses on a specific layer or functionality:

1.  **Phase 1: Data Definition (Backend)**
    *   **Task:** Define Daily Mission Data Schema (`backend/models/daily_mission.py`).
    *   **Rationale:** Establish the foundational data structure before implementing logic that depends on it. This ensures clarity on data fields, types, and indexes.

2.  **Phase 2: Core Service Logic (Backend)**
    *   **Task:** Create Daily Mission Generation Service (`backend/services/mission_service.py`).
    *   **Rationale:** Implement the core business logic for creating daily missions. This service will be a central piece used by other parts of the backend (APIs, jobs).

3.  **Phase 3: API Exposure (Backend)**
    *   **Task:** Create Mission Retrieval API Endpoint (`backend/routes/missions.py`).
    *   **Rationale:** Expose the mission data to the frontend. This step makes the backend functionality usable by a client application.

4.  **Phase 4: Frontend Integration (Frontend)**
    *   **Task:** Integrate Mission API into React Native App (`frontend/screens/HomeScreen.tsx`).
    *   **Rationale:** Connect the frontend to the backend to display missions to the user. This is the first point of end-to-end feature validation.

5.  **Phase 5: Frontend State & UX (Frontend)**
    *   **Task:** Handle Mission Resume on Reopen (`frontend/screens/MissionScreen.tsx`).
    *   **Rationale:** Improve user experience by allowing users to continue missions from where they left off. This involves persisting mission progress (current question, answers) via the backend and restoring this state when the user returns to the mission.

6.  **Phase 6: Automation & Maintenance (Backend)**
    *   **Task:** Implement Daily Reset Backend Job (`backend/jobs/daily_reset.py`).
    *   **Rationale:** Automate the daily process of resetting missions (by archiving old, incomplete ones), ensuring the feature operates continuously without manual intervention. This was implemented using an in-app scheduler (APScheduler).

## Architectural Decisions & Trade-offs

Based on the [Implementation Plan](Requirement/userstory/story1/implementation_plan.md) and current codebase:

*   **Technology Choices:**
    *   **FastAPI (Python) for Backend:** Chosen for its high performance with asynchronous capabilities, Pydantic-based data validation, and automatic API documentation. This is suitable for building robust and quick APIs.
    *   **React Native for Frontend:** Enables cross-platform mobile app development from a single codebase.
    *   **MongoDB for Database:** Offers flexibility with its NoSQL, document-based structure, fitting for evolving schemas. The plan mentions Mongoose (JS-specific); Python will use a driver like Motor or PyMongo, with Pydantic models serving a similar schema-definition role as Mongoose schemas.
    *   **Decision:** Standard, modern choices for their respective domains, balancing development speed and performance.
*   **Modular Design:**
    *   Separation of concerns is emphasized: `models` for data schema, `services` for business logic, `routes` for API endpoints.
    *   **Decision:** Enhances maintainability, testability, and reusability of code.
*   **Mocking & Testing:**
    *   The `mission_service.py` utilizes an in-memory list (`_mock_db_missions`) of `DailyMissionDocument` objects for simulating database interactions. This was updated from a simple dictionary to better reflect the data structures.
    *   **Trade-off:** Simplifies initial development and testing. Full integration tests with a test database instance will be necessary later.
*   **User Authentication (LINE Login):**
    *   Planned but not yet fully implemented in early tasks. API endpoints currently simulate user context (e.g., `get_current_user_id` in `backend/routes/missions.py`).
    *   **Decision:** Allows core feature development to proceed without being blocked by authentication setup. Real authentication will be layered in.
*   **Question Pool as CSV:**
    *   Initially, questions are loaded from a CSV (`backend/data/gat_questions.csv`).
    *   **Trade-off:** Easy to start with and manage for a small number of questions. Less scalable and manageable than a database solution for a large question pool.
*   **Timezone Handling (UTC+7):**
    *   Explicitly defined `TARGET_TIMEZONE = timezone(timedelta(hours=7))` in `backend/services/mission_service.py`.
    *   Mission dates are handled with respect to this timezone, often by converting to UTC for storage/comparison (e.g., `get_utc7_today_midnight_utc0`).
    *   **Decision:** Crucial for features like daily resets that depend on a specific local time.
*   **Frontend-Backend Contract:** Clear API definitions are important. Using Pydantic models in FastAPI (e.g., `DailyMissionDocument`, generic `MissionResponse`, `MissionProgressUpdatePayload`) and corresponding TypeScript interfaces in the frontend helps maintain this contract for features like fetching missions with progress and updating progress.
*   **Background Jobs (Daily Reset):**
    *   Implemented using APScheduler integrated into the FastAPI application (`backend/main.py`) to run the job defined in `backend/jobs/daily_reset.py`.
    *   **Decision:** In-app scheduling chosen for ease of environment management and direct access to application services. This is suitable for the current scale and complexity. An external cron system could be considered if jobs become more numerous or resource-intensive, requiring decoupling.
    *   **Trade-off:** If the application scales to multiple instances, care must be taken to ensure scheduled jobs run as intended (e.g., only on one instance or by using distributed locking if the job isn't idempotent, though the current archival job is designed to be idempotent).

## Constraints & Considerations

*   **Focus on MVP:** The initial tasks are geared towards delivering the core Daily Mission feature.
*   **Test Coverage:** Each task in the implementation plan specifies requirements for automated tests (unit and integration) and manual verification.
*   **Scalability:** While initial mocks are used, the choice of FastAPI and MongoDB is conducive to future scaling.
*   Migration from mock DB in `mission_service.py` to a real MongoDB instance.
*   Comprehensive error logging and monitoring.
*   More sophisticated mission generation logic (e.g., personalized missions based on user performance).
*   Ensuring robust behavior of the in-app scheduler in a scaled environment (if applicable in the future).
*   CI/CD pipelines for automated testing and deployment.

## Future Work (Inferred & Potential)

*   Full implementation of LINE Login for authentication.
*   Migration of the Question Pool from CSV to a database for better management and scalability.
*   Migration from mock DB in `mission_service.py` to a real MongoDB instance.
*   Comprehensive error logging and monitoring.
*   More sophisticated mission generation logic (e.g., personalized missions based on user performance).
*   CI/CD pipelines for automated testing and deployment.
*   Setting up a proper staging/production environment with a real MongoDB instance.

For API specific details, see [API Contracts](api_contracts.md). 