from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from agents import GeneratorAgent, ReviewerAgent
from typing import List, Dict, Optional
import os

app = FastAPI(title="AI Assessment Agent API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from models import AssessmentRequest, GeneratorInput, GeneratorOutput, ReviewerOutput

generator = GeneratorAgent()
reviewer = ReviewerAgent()

@app.get("/")
async def root():
    return FileResponse("index.html")

# Serve static assets (CSS/JS)
@app.get("/style.css")
async def styles():
    return FileResponse("style.css")

@app.get("/script.js")
async def scripts():
    return FileResponse("script.js")

@app.post("/generate-assessment")
async def generate_assessment(request: AssessmentRequest):
    steps = []
    
    # Step 1: Initial Generation
    gen_input = GeneratorInput(grade=request.grade, topic=request.topic)
    initial_content = generator.generate(gen_input)
    steps.append({
        "agent": "Generator Agent",
        "action": "Initial Generation",
        "output": initial_content.model_dump()
    })
    
    # Step 2: Review
    review_result = reviewer.review(initial_content, request.grade, request.topic)
    steps.append({
        "agent": "Reviewer Agent",
        "action": "Content Review",
        "output": review_result.model_dump()
    })
    
    final_content = initial_content
    refined = False
    
    # Step 3: Refinement (Limit to one pass)
    if review_result.status == "fail":
        refine_input = GeneratorInput(
            grade=request.grade, 
            topic=request.topic, 
            feedback=review_result.feedback
        )
        refined_content = generator.generate(refine_input)
        final_content = refined_content
        refined = True
        steps.append({
            "agent": "Generator Agent",
            "action": "Refined Generation",
            "output": refined_content.model_dump()
        })
    
    return {
        "grade": request.grade,
        "topic": request.topic,
        "refined": refined,
        "final_content": final_content.model_dump(),
        "steps": steps
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
