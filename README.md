# AI Assessment Agent System

A multi-agent AI system designed to generate, review, and refine educational content. This project features a **Generator Agent** and a **Reviewer Agent** working in a loop to ensure content is age-appropriate and pedagogically sound.

## Features

- **Multi-Agent Workflow**: 
  - `Generator Agent`: Drafts content (Explanation + MCQs).
  - `Reviewer Agent`: Validates content against age, curriculum, and clarity standards.
- **Auto-Refinement**: If the Reviewer fails the content, the Generator automatically refines it based on feedback.
- **Live Visualization**: A web-based UI (`index.html`) visualizes the agent interaction in real-time.
- **Strict Logic**: Enforces "Introduce before Testing" rules (no questions on concepts not explained).

## Setup & Installation

1.  **Prerequisites**:
    - Python 3.10+
    - Google Gemini API Key

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key**:
    - Create a `.env` file in the root directory.
    - Add your key:
      ```
      GOOGLE_API_KEY=your_actual_api_key_here
      ```
    - *Note: If no key is provided, the system runs in Mock Mode for demonstration.*

## How to Run

1.  **Start the FastAPI Server**:
    Run the orchestrator script:
    ```bash
    python main.py
    ```
    *Alternative (standard FastAPI command):*
    ```bash
    uvicorn main:app --reload
    ```
    The backend will start at `http://localhost:8000`.

2.  **Access the Dashboard**:
    Open your browser and navigate to:
    **[http://localhost:8000](http://localhost:8000)**

3.  **Test It**:
    - Enter a **Grade** (e.g., 4) and **Topic** (e.g., "Photosynthesis").
    - Click **Run Pipeline**.
    - Watch the agents collaborate!

## Project Structure

- `main.py`: FastAPI backend and orchestration logic.
- `agents.py`: AI Agent definitions and prompts.
- `models.py`: Pydantic data models for structured I/O.
- `index.html`, `style.css`, `script.js`: Frontend UI.
