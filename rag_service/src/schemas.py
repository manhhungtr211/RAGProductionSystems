from pydantic import BaseModel


class RetrievalInput(BaseModel):
    user_input: str
    section_id: str
