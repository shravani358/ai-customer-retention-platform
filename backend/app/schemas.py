from pydantic import BaseModel


class CustomerCreate(BaseModel):
    name: str
    email: str = ""
    tenure_months: int = 0
    monthly_charges: float = 0.0
    support_tickets: int = 0
    last_login_days: int = 0
    churn_risk: float = 0.0


class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    tenure_months: int
    monthly_charges: float
    support_tickets: int
    last_login_days: int
    churn_risk: float

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "analyst"


class UserOut(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    history: list[ChatMessage]