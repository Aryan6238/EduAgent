from pydantic import BaseModel, Field
from typing import List

class MCQ(BaseModel):
    question: str
    options: List[str] = Field(..., min_items=4, max_items=4)
    answer: str

class GeneratorOutput(BaseModel):
    explanation: str
    mcqs: List[MCQ]

class ReviewerOutput(BaseModel):
    status: str # "pass" or "fail"
    feedback: List[str]

class GeneratorInput(BaseModel):
    grade: int
    topic: str
    feedback: List[str] = []

class AssessmentRequest(BaseModel):
    grade: int
    topic: str
