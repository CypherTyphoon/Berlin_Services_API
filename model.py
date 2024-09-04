from sqlmodel import SQLModel, Field

class Service(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    digital_service: bool
    responsible_office: str