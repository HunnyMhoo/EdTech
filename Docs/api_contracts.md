# API Contracts

This document provides details on the public and internal APIs available in the EdTech Platform backend. As the system evolves, this document will be updated to reflect new endpoints and changes.

## Conventions

-   **Base URL:** All API endpoints are prefixed with `/api` (e.g., `http://127.0.0.1:8000/api`).
-   **Authentication:** Currently simulated via a hardcoded user ID (`test_user_123`). Future implementation will use LINE Login (OAuth 2.0 bearer tokens).
-   **Response Format:** Standardized JSON responses using the `MissionResponse` model where applicable (`status`, `data`, `message`).
-   **Error Handling:** Uses standard HTTP status codes. Errors from FastAPI often return a JSON object with a `detail` field.

## Public APIs

These APIs are intended to be consumed by the frontend client (React Native app).

### Missions API

-   **Router Source:** [`backend/routes/missions.py`](../backend/routes/missions.py)
-   **Tag in OpenAPI:** `Missions`

#### 1. Get Today's Mission

*   **Description:** Retrieves the daily mission for the currently authenticated user for today (UTC+7). This now includes mission progress fields like `current_question_index` and `answers`.
*   **Method:** `GET`
*   **Path:** `/missions/today`
*   **Purpose:** Allows the frontend to fetch and display the user's current daily mission.
*   **Parameters:**
    *   None (User ID is derived from the authentication context - currently a hardcoded dependency `get_current_user_id`).
*   **Responses:**
    *   **`200 OK` (Success):**
        *   **Body:** `MissionResponse[DailyMissionDocument]` model
            ```json
            {
                "status": "success",
                "data": {
                    "user_id": "string",
                    "date": "YYYY-MM-DD string",
                    "question_ids": ["string"],
                    "status": "string (e.g., not_started, in_progress, complete)",
                    "current_question_index": 0,
                    "answers": [{"question_id": "string", "answer": "any"}],
                    "created_at": "datetime string (ISO 8601)",
                    "updated_at": "datetime string (ISO 8601)"
                },
                "message": "Today's mission retrieved successfully."
            }
            ```
        *   The `data` field contains a `DailyMissionDocument` schema object (defined in `backend.models.daily_mission.DailyMissionDocument`).
    *   **`404 Not Found` (Error):**
        *   **Body:**
            ```json
            {
                "detail": "No mission found for user {user_id} for today (UTC+7)."
            }
            ```
    *   **`500 Internal Server Error` (Error):**
        *   **Body:**
            ```json
            {
                "detail": "An unexpected error occurred: {error_message}"
            }
            ```
*   **Code Reference:** `get_today_mission_for_current_user` function in [`backend/routes/missions.py`](../backend/routes/missions.py).

#### 2. Update Today's Mission Progress

*   **Description:** Updates the progress (current question index, answers, and status) of the daily mission for the currently authenticated user.
*   **Method:** `PUT`
*   **Path:** `/missions/today/progress`
*   **Purpose:** Allows the frontend to save the user's progress as they interact with the mission.
*   **Parameters:**
    *   User ID is derived from the authentication context.
    *   **Request Body:** `MissionProgressUpdatePayload` model
        ```json
        {
            "current_question_index": 0,
            "answers": [{"question_id": "string", "answer": "any"}],
            "status": "string (e.g., in_progress, complete)" // Optional
        }
        ```
*   **Responses:**
    *   **`200 OK` (Success):**
        *   **Body:** `MissionResponse[DailyMissionDocument]` model (containing the updated mission document)
            ```json
            {
                "status": "success",
                "data": { // Updated DailyMissionDocument ... },
                "message": "Mission progress updated successfully."
            }
            ```
    *   **`404 Not Found` (Error):**
        *   **Body:**
            ```json
            {
                "detail": "Failed to update progress for user {user_id}. Mission for today not found or update failed."
            }
            ```
    *   **`422 Unprocessable Entity` (Error):**
        *   If request payload validation fails (FastAPI default).
    *   **`500 Internal Server Error` (Error):**
        *   **Body:**
            ```json
            {
                "detail": "An unexpected error occurred while updating progress: {error_message}"
            }
            ```
*   **Code Reference:** `update_today_mission_progress` function in [`backend/routes/missions.py`](../backend/routes/missions.py).

---

### Health Check API

-   **Router Source:** [`backend/main.py`](../backend/main.py)
-   **Tag in OpenAPI:** `Health Check`

#### 1. Health Check

*   **Description:** Simple endpoint to verify if the API server is running and healthy.
*   **Method:** `GET`
*   **Path:** `/health`
*   **Purpose:** Used for monitoring and operational checks.
*   **Parameters:** None.
*   **Responses:**
    *   **`200 OK` (Success):**
        *   **Body:**
            ```json
            {
                "status": "ok",
                "message": "API is healthy"
            }
            ```
*   **Code Reference:** `health_check` function in [`backend/main.py`](../backend/main.py).

---

## Internal APIs/Service Functions

While not strictly HTTP APIs, the backend services expose functions that act as internal contracts between components.

### Mission Service

-   **Source:** [`backend/services/mission_service.py`](../backend/services/mission_service.py)

#### 1. `get_todays_mission_for_user(user_id: str) -> Optional[DailyMissionDocument]`

*   **Description:** Retrieves today's (UTC+7) mission for a given user from the data store, including progress fields.
*   **Parameters:**
    *   `user_id (str)`: The ID of the user.
*   **Returns:** A `DailyMissionDocument` Pydantic model instance if a mission is found, otherwise `None`.
*   **Called by:** The `/missions/today` API endpoint.

#### 2. `generate_daily_mission(user_id: str, current_datetime_utc: Optional[datetime] = None) -> DailyMissionDocument`

*   **Description:** Generates and persists a new daily mission with 5 questions for the user. Returns a `DailyMissionDocument`.
*   **Parameters:**
    *   `user_id (str)`: The user's ID.
    *   `current_datetime_utc (Optional[datetime])`: For testing, to simulate a specific time.
*   **Returns:** A `DailyMissionDocument` instance.
*   **Raises:** `MissionAlreadyExistsError`, `NoQuestionsAvailableError`.

#### 3. `update_mission_progress(user_id: str, current_question_index: int, answers: List[Dict[str, Any]], status: Optional[MissionStatus] = None) -> Optional[DailyMissionDocument]`

*   **Description:** Updates the progress of today's mission for a given user.
*   **Parameters:**
    *   `user_id (str)`: The user's ID.
    *   `current_question_index (int)`: The current question index.
    *   `answers (List[Dict[str, Any]])`: The list of answers provided by the user.
    *   `status (Optional[MissionStatus])`: The new mission status (e.g., `in_progress`, `complete`).
*   **Returns:** The updated `DailyMissionDocument` instance if successful, otherwise `None` (e.g., if the mission doesn't exist).
*   **Called by:** The `/missions/today/progress` API endpoint.

For a list of components, see the [Component Reference](component_reference.md). 