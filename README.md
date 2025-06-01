# EdTech Platform

## Overview

The EdTech Platform aims to enhance the learning experience by providing daily engaging missions and educational content to students. It's designed to be a modular and scalable system supporting interactive learning modules, with an initial focus on a Daily Mission feature for GAT เชื่อมโยง practice for Thai high school students.

## Features

*   **Daily Mission Generation**: Generates 5 unique daily questions per user.
*   **User-Specific Mission Retrieval**: Delivers missions through an API endpoint.
*   **Mission Progress Tracking**: Allows users to save and resume mission progress.
*   **Timezone-Specific Content**: Missions are aligned with UTC+7 for the target audience.
*   **Automated Daily Reset**: Archives old, incomplete missions daily.
*   **Frontend Mission Display**: Presents missions to users for interaction.

## Technology Stack

*   **Backend**:
    *   Framework: Python with FastAPI
    *   Database: MongoDB (currently mocked in-memory, planned for actual instance)
    *   Scheduling: APScheduler (for background jobs)
    *   Data Validation: Pydantic
*   **Frontend**:
    *   Framework: React Native (TypeScript)
*   **Documentation**: Extensive Markdown documentation in the `/Docs` directory.

## Project Structure

```
EdTech/
├── backend/            # Python FastAPI backend
│   ├── data/           # Data files (e.g., question CSVs)
│   ├── jobs/           # Background job definitions (e.g., daily reset)
│   ├── models/         # Pydantic data models
│   ├── routes/         # API route definitions
│   ├── services/       # Business logic services
│   ├── tests/          # Backend tests (unit, integration)
│   └── main.py         # FastAPI application entry point
├── frontend/           # React Native frontend
│   ├── screens/        # React Native screen components
│   ├── services/       # Frontend API services and type definitions
│   └── __tests__/      # Frontend tests (currently for services)
├── Docs/               # Project documentation
├── .giga/              # Giga AI related files
├── .cursorrules        # Cursor rules
└── README.md           # This file
```

## Setup and Installation

### Prerequisites

*   Python 3.8+ (for backend)
*   Node.js and npm/yarn (for frontend - React Native development environment)
*   An appropriate IDE (e.g., VS Code)
*   Git

### Backend Setup

1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```
2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies**:
    *A `requirements.txt` file is needed. Assuming one is created with FastAPI, Uvicorn, APScheduler, Pydantic, etc.*
    ```bash
    pip install -r requirements.txt
    ```
    *(If no `requirements.txt` exists, you'll need to install them manually: `pip install fastapi uvicorn[standard] apscheduler pydantic`)*

### Frontend Setup

1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```
2.  **Install dependencies**:
    *A `package.json` file is needed. If it exists:*
    ```bash
    npm install
    # OR
    yarn install
    ```
    *(If no `package.json` exists, this React Native project is not fully initialized. You would typically run `npx react-native init EdTechFrontend` or similar, but since files exist, a `package.json` needs to be carefully crafted or generated based on existing `.tsx` files and common React Native dependencies like `react`, `react-native`.)*

## Running the Application

### Backend

1.  Ensure your Python virtual environment is activated and you are in the `EdTech/` root or `backend/` directory.
2.  If in the project root, and your `PYTHONPATH` is set up (e.g. `export PYTHONPATH=.`), you can run:
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```
    Alternatively, from the `backend/` directory:
    ```bash
    uvicorn main:app --reload --port 8000
    ```
3.  The backend API should now be running at `http://localhost:8000`.
4.  You can access the health check at `http://localhost:8000/health`.
5.  API documentation (Swagger UI) should be available at `http://localhost:8000/docs`.

### Frontend

*(These instructions assume a `package.json` with appropriate scripts exists in `frontend/`)*

1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```
2.  **Start the Metro Bundler**:
    ```bash
    npx react-native start
    # OR
    npm start
    # OR
    yarn start
    ```
3.  **Run on a simulator/device**:
    *   For iOS (macOS only, Xcode required):
        ```bash
        npx react-native run-ios
        ```
    *   For Android (Android Studio and SDK required):
        ```bash
        npx react-native run-android
        ```

## API Documentation

*   The backend API is built with FastAPI, which provides automatic interactive documentation.
*   Once the backend is running, access it at: `http://localhost:8000/docs`
*   Detailed API contracts are also available in [`Docs/api_contracts.md`](./Docs/api_contracts.md).

## Testing

### Backend Tests

1.  Navigate to the `backend/` directory.
2.  Ensure testing dependencies (e.g., `pytest`, `httpx`) are installed.
3.  Run tests (example using pytest):
    ```bash
    pytest
    ```
    *(Specific commands might vary based on test runner configuration.)*
    *   Unit tests are in `backend/tests/unit/`.
    *   Integration tests are in `backend/tests/integration/`.

### Frontend Tests

1.  Navigate to the `frontend/` directory.
2.  Ensure testing dependencies (e.g., Jest) are installed via `package.json`.
3.  Run tests (example using npm/yarn script, assuming it's defined in `package.json`):
    ```bash
    npm test
    # OR
    yarn test
    ```
    *   Service tests are in `frontend/services/__tests__/`.

## Contributing

(Placeholder for contribution guidelines - e.g., branching strategy, code style, pull request process.)

## License

(Placeholder for project license - e.g., MIT, Apache 2.0.)

---
*This README was generated by Giga AI based on project analysis.* 