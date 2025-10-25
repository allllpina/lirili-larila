from typing import List, Literal

from config import get_settings
from google import genai
from pydantic import BaseModel

settings = get_settings()


class TaskPriority(BaseModel):
    task_id: str
    priority: Literal["low", "medium", "high"]


class ExpectedResponse(BaseModel):
    prioritized_tasks: List[TaskPriority]
    recommendations: List[str]


class GoogleAIProcessor:
    @staticmethod
    async def get_priority_and_recomendations(content: dict):
        client = genai.Client(api_key=settings.google_ai_api_key.get_secret_value())

        prompt = f"""
        You are an expert project management assistant.
        Analyze the following project data (in JSON format).

        Your task:
            1.  **Assign Priority**: Find all tasks where the "priority" field has a value of `null` (or `None`).
            2.  **Logic**: Based on the overall project information, determine the priority of the task.
            3.  **Constraints**: Allowed priority values are: "low", "medium", or "high".
            4.  **Recommendations**: Provide 2-3 general, useful recommendations for the successful completion
            of the project.

            You MUST return the response exclusively as a SINGLE valid JSON object.
            Do not add any text before or after the JSON (e.g., ```json).

            Expected JSON response structure:
            {{
            "prioritized_tasks": {{
                "task_id_1": "assigned_priority",
                "task_id_2": "assigned_priority"
            }},
            "recommendations": [
                "First recommendation...",
                "Second recommendation..."
            ]
            }}

            Here is the project data:
            {content}"""

        response = await client.aio.models.generate_content(
            model=settings.google_model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ExpectedResponse,
            },
        )

        return response
