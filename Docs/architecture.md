# EdTech Platform Architecture

This document outlines the architecture of the EdTech Platform, focusing on its key components and how they interact.

## System Diagram

The following diagram illustrates the major components and data flow within the system:

```mermaid
graph TD
    A[Frontend: React Native App] -- HTTPS (API Calls) --> B{Backend: FastAPI Server};
    B -- CRUD Operations (Async) --> C[(Database: MongoDB)];
    D[LINE Login Service] -- OAuth 2.0 Flow --> A;
    B -- Authentication Check --> D;
    E[Question Pool: CSV/DB] -- Data Source --> B;
    F[In-App Scheduler (APScheduler)] -.-> B; # Scheduler triggers job within Backend
    F -- Manages --> G{Daily Reset Job};
    G -- Modifies Mission Status --> C;

    subgraph User Interaction
        A
    end

    subgraph Backend Services
        B
        E
        F
        G
    end

    subgraph Data Storage
        C
    end

    subgraph External Services
        D
    end
```

## Component Responsibilities & Data Flow

1.  **Frontend (React Native App):**
    *   **Responsibility:** User interface and interaction. Displays missions, captures user input, and manages local app state.
    *   **Tech Stack:** React Native.
    *   **Data Flow:**
        *   Makes HTTPS API calls (primarily JSON) to the Backend (FastAPI) for data (e.g., fetching missions, submitting answers).
        *   Interacts with LINE Login Service for user authentication via OAuth 2.0.
        *   Receives and displays data from the backend.
        *   Flows are primarily asynchronous (e.g., `useEffect` hooks for API calls).

2.  **Backend (FastAPI Server):**
    *   **Responsibility:** Business logic, data processing, API provision, and interaction with the database and external services.
    *   **Tech Stack:** Python, FastAPI.
    *   **Data Flow:**
        *   Receives API requests from the Frontend.
        *   Handles user authentication (planned integration with LINE Login).
        *   Performs CRUD (Create, Read, Update, Delete) operations on the MongoDB database to manage user data, missions, etc. These operations are generally asynchronous thanks to FastAPI and suitable database drivers (e.g., Motor for MongoDB).
        *   Fetches data from the Question Pool (e.g., `gat_questions.csv` or a dedicated table/collection) to generate missions.
        *   Hosts an in-app scheduler (APScheduler) that triggers background jobs (e.g., daily mission archival).
        *   Returns structured JSON responses to the Frontend.

3.  **Database (MongoDB):**
    *   **Responsibility:** Persistent storage of application data, including user profiles, daily missions, question statuses, etc.
    *   **Tech Stack:** MongoDB. The implementation plan mentions using Mongoose (which is for Node.js/JavaScript); for Python, a library like `Motor` (async) or `PyMongo` (sync/async) would be used with Pydantic models for schema definition as seen in `backend/models/daily_mission.py` (planned) and `backend/services/mission_service.py`.
    *   **Data Flow:** Accessed by the Backend (FastAPI) for all data storage and retrieval needs.

4.  **Question Pool (CSV/DB):**
    *   **Responsibility:** Stores the questions used for generating daily missions.
    *   **Tech Stack:** Currently a CSV file (`backend/data/gat_questions.csv`), but could be migrated to a dedicated database table/collection for better management.
    *   **Data Flow:** Read by the Backend (FastAPI) when generating new missions.

5.  **LINE Login Service (External):**
    *   **Responsibility:** Handles user authentication via OAuth 2.0.
    *   **Data Flow:** The Frontend initiates the login flow with LINE. The Backend will verify tokens received from the Frontend.

6.  **In-App Scheduler (APScheduler):**
    *   **Responsibility:** Manages and executes scheduled background tasks within the backend application.
    *   **Tech Stack:** APScheduler library integrated into FastAPI.
    *   **Data Flow:** Triggers the Daily Reset Job at a configured time. The job itself interacts with the Mission Service and Database to archive old missions.

## Asynchronous vs. Synchronous Flows

-   **Frontend-Backend Communication:** Inherently asynchronous (HTTP requests).
-   **Backend Internal Operations:** FastAPI encourages asynchronous operations (`async`/`await`) for I/O-bound tasks like database queries (`_fetch_mission_from_db` in `mission_service.py`) and external API calls. This is crucial for performance and scalability.
-   **Database Interaction:** When using an async driver like `Motor` with MongoDB, database operations are non-blocking.

For details on how features are planned to be built, refer to the [Implementation Strategy](implementation_strategy.md). 