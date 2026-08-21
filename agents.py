import os
import json
from typing import Dict, List
import google.generativeai as genai
from models import GeneratorInput, GeneratorOutput, ReviewerOutput, MCQ

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class GeneratorAgent:
    """
    Responsibility: Generate draft educational content for a given grade and topic.
    """
    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        self.use_mock = not GOOGLE_API_KEY
        if not self.use_mock:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(model_name)

    def generate(self, input_data: GeneratorInput) -> GeneratorOutput:
        if self.use_mock:
            return self._mock_generate(input_data)
        
        prompt = f"""
        Act as a child-friendly educational content creator. 
        Your ONLY responsibility is to generate draft learning material for Grade {input_data.grade} students on the topic: "{input_data.topic}".
        
        Classroom Logic Rules:
        1. INTRODUCE BEFORE TESTING: Your explanation MUST cover every concept that appears in the MCQs. Do not ask about things you didn't explain.
        2. NO UNEXPLAINED CONCEPTS: The MCQs must be strictly derived from the text provided in the explanation.
        3. GRADE-APPROPRIATE VOCABULARY: Avoid advanced terms or jargon that a Grade {input_data.grade} student wouldn't know. If you must use a new word, explain it simply.
        4. SIMPLE STRUCTURE: Use short, clear sentences.
        5. CONCISE: Keep the draft engaging and brief.
        
        The output must be a valid JSON object matching this schema:
        {{
            "explanation": "A simple, child-friendly explanation that introduces all necessary concepts.",
            "mcqs": [
                {{
                    "question": "A question based ONLY on the explanation above.",
                    "options": ["string", "string", "string", "string"],
                    "answer": "the correct option"
                }}
            ]
        }}
        """
        
        if input_data.feedback:
            prompt += f"\n\nRefinement Feedback from Teacher (Reviewer):\n" + "\n".join([f"- {i}" for i in input_data.feedback])
            prompt += f"\n\nIMPORTANT: Use this feedback to fix any classroom logic errors. Ensure Grade {input_data.grade} appropriateness."

        try:
            response = self.model.generate_content(prompt)
            data = self._parse_json(response.text)
            return GeneratorOutput(**data)
        except Exception as e:
            return GeneratorOutput(
                explanation=f"Oh no! I had a little trouble with my lesson plan. (Error: {str(e)})",
                mcqs=[]
            )

    def _parse_json(self, text: str) -> Dict:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text)

    def _mock_generate(self, input_data: GeneratorInput) -> GeneratorOutput:
        topic_lower = input_data.topic.lower()
        if "angle" in topic_lower:
            if input_data.grade > 6:
                # Advanced Mock for High School
                if input_data.feedback:
                    return GeneratorOutput(
                        explanation=f"At the Grade {input_data.grade} level, we transition from basic shapes to the trigonometric properties of angles. An angle is a measure of rotation between two rays. We often measure them in Radians. Key concepts include Supplementary angles (sum to 180°) and the use of the Sine rule for non-right triangles.",
                        mcqs=[
                            MCQ(question="If two angles are supplementary, what is their sum in degrees?", options=["90°", "180°", "270°", "360°"], answer="180°"),
                            MCQ(question="Which trigonometric ratio relates the opposite side to the hypotenuse?", options=["Sine", "Cosine", "Tangent", "Secant"], answer="Sine"),
                            MCQ(question="How many radians are equivalent to a full 360° turn?", options=["π", "2π", "π/2", "3π"], answer="2π")
                        ]
                    )
                return GeneratorOutput(
                    explanation=f"Welcome to Grade {input_data.grade} Mathematics. Today we explore advanced angle theorems and trigonometry.",
                    mcqs=[MCQ(question="What is the unit used in trigonometry for measuring rotation?", options=["Grams", "Liters", "Radians", "Watts"], answer="Radians")]
                )
            else:
                # Simple Mock for Elementary/Middle School
                if input_data.feedback:
                    return GeneratorOutput(
                        explanation=f"An angle is the space between two lines that meet at a point called a vertex. In Grade {input_data.grade}, we look at three main angles. A 'Right Angle' is square like a book corner. An 'Acute Angle' is smaller and sharp. An 'Obtuse Angle' is wider and bigger. Remember: Acute is small (and 'a-cute' little thing!), and Obtuse is large!",
                        mcqs=[
                            MCQ(question="What is the point called where two lines meet to make an angle?", options=["Edge", "Vertex", "Corner", "Base"], answer="Vertex"),
                            MCQ(question="Which angle is the same shape as the corner of a square book?", options=["Acute", "Obtuse", "Right", "Straight"], answer="Right"),
                            MCQ(question="If an angle is smaller than a right angle, what is it called?", options=["Acute", "Obtuse", "Wide", "Large"], answer="Acute")
                        ]
                    )
                return GeneratorOutput(
                    explanation=f"Hello! Today we are learning about angles for Grade {input_data.grade}. An angle is a way to measure a turn. When two lines meet at a point, they make an angle!",
                    mcqs=[MCQ(question="What is an angle used to measure?", options=["Weight", "Length", "A turn", "Speed"], answer="A turn")]
                )
        
        # General Mock
        return GeneratorOutput(
            explanation=f"Welcome to our Grade {input_data.grade} lesson on {input_data.topic}! We will explore how this works using simple words and examples.",
            mcqs=[MCQ(question=f"What is the main topic of our lesson today?", options=["Math", "Reading", input_data.topic, "History"], answer=input_data.topic)]
        )

class ReviewerAgent:
    """
    Responsibility: Evaluate the Generator’s output.
    """
    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        self.use_mock = not GOOGLE_API_KEY
        if not self.use_mock:
            self.model = genai.GenerativeModel(model_name)

    def review(self, content: GeneratorOutput, grade: int, topic: str) -> ReviewerOutput:
        if self.use_mock:
            return self._mock_review(content, grade, topic)
        
        prompt = f"""
        Act as a strict but friendly teacher reviewing educational content for Grade {grade} students.
        Topic: "{topic}"
        
        Content to review:
        {content.model_dump_json(indent=2)}
        
        Review Criteria:
        1. AGE APPROPRIATENESS: Is the language and vocabulary perfect for Grade {grade}? Are there any terms too advanced for this level?
        2. CURRICULUM ALIGNMENT: Is this TOPIC actually taught at this grade level? (e.g. 'Types of Angles' is Grade 4+, not Grade 1). If the topic is too advanced, FAIL it and ask the generator to pivot to a simpler related concept (e.g. just 'Corners' for Grade 1).
        3. CONCEPTUAL CORRECTNESS: Is the information 100% factually accurate for this level?
        4. CLARITY: Is the explanation clear? Does the explanation cover EVERY concept mentioned in the MCQs (Introduce before test)?
        
        Return a JSON object:
        {{
            "status": "pass" or "fail",
            "feedback": ["Detailed, friendly feedback about specific classroom logic errors or praise"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            data = self._parse_json(response.text)
            return ReviewerOutput(**data)
        except Exception as e:
            return ReviewerOutput(status="fail", feedback=[f"Error in review: {str(e)}"])

    def _parse_json(self, text: str) -> Dict:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text)

    def _mock_review(self, content: GeneratorOutput, grade: int, topic: str) -> ReviewerOutput:
        # Check for length/detail first
        if len(content.explanation) < 150:
            return ReviewerOutput(
                status="fail",
                feedback=[f"The explanation for Grade {grade} needs more detail!", f"Please add more examples of {topic}."]
            )
        
        # Check for Grade Complexity (Demonstration only)
        if grade > 6 and "book corner" in content.explanation.lower():
            return ReviewerOutput(
                status="fail",
                feedback=[f"This content is too simplistic for a Grade {grade} student.", "Please use more advanced terminology like 'Radians' or 'Supplementary angles' instead of 'book corners'."]
            )
            
        return ReviewerOutput(status="pass", feedback=["Great work! This is perfect for Grade " + str(grade)])
