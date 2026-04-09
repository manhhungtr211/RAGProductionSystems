from pydantic import BaseModel
from typing import Optional


class RetrievalInput(BaseModel):
    user_input: str
    session_id: str
    user_id: Optional[str] = "anonymous"
