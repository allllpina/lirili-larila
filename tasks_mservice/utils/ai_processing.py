from typing import List, Literal

from api.schemas import FullProject
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
    async def get_priority_and_recomendations(content: FullProject) -> ExpectedResponse:
        client = genai.Client(api_key=settings.google_ai_api_key.get_secret_value())

        prompt = f"""
        You are an expert project management assistant with strict adherence to data integrity.
        Analyze the following project data (in JSON format).

        *** CRITICAL INSTRUCTION ***
        You are STRICTLY FORBIDDEN from modifying, re-evaluating, or outputting tasks where the "priority" field is 
        already set (i.e., not null).
        Existing priorities are IMMUTABLE. You must only act on tasks where priority is explicitly `null` or `None`.

        Your task:
            1.  **Identify Targets**: Scan the data and isolate ONLY the tasks where "priority" is `null`.
            2.  **Assign Priority**: Analyze the context and assign a priority ONLY to these isolated tasks.
            3.  **Constraints**: Allowed priority values are: "low", "medium", or "high".
            4.  **Recommendations**: Provide 3-5 general, useful recommendations for the successful completion
            of the project.

            You MUST return the response exclusively as a SINGLE valid JSON object.
            Do not add any text before or after the JSON (no markdown formatting like ```json).

            Expected JSON response structure:
            {{
            "prioritized_tasks": {{
                "task_id_X": "assigned_priority",
                "task_id_Y": "assigned_priority"
                // IMPORTANT: This object must ONLY contain tasks that were originally null.
                // Do NOT include tasks that already had a priority.
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

        if response.parsed:
            return response.parsed

        raise ValueError("AI failed to return structured data")
