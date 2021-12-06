from pydantic import BaseModel

class Reset_Password_Schema(BaseModel):
    newPassword1: str
    newPassword2: str
    token: str

class SignUpSchema(BaseModel):
    username: str
    email: str
    password: str

