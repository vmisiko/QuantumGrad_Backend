from enum import unique
from passlib.hash import bcrypt
from tortoise import fields 
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model 


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    email =fields.CharField(128, unique=True)
    password = fields.CharField(128)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_verified = fields.BooleanField(default= False)
    email_verification_date = fields.DatetimeField(null= True)
    is_activated = fields.BooleanField(default=False)


    def verify_password(self, password):
        return bcrypt.verify(password, self.password)

    class Meta:
        table: str = 'users'

User_Pydantic = pydantic_model_creator(User, name='User')
UserOut_Pydantic = pydantic_model_creator(User, name='UserOut', exclude=('password',))
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)
Signup_Pydantic = pydantic_model_creator(
    User,
    name='Signup', 
    exclude=(
        'password',
        'created_at',
        'is_verified',
        'email_verification_date',
        'is_activated',
    )
)

