from pydantic import BaseModel, EmailStr, model_validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError('Пароли не совпадают')
        return self