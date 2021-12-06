import jwt
from typing import List, Optional, Dict

from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from starlette.types import Message
from tortoise.query_utils import Q
from config import settings
from config.settings import get_settings
from services.auth import Auth
from services.mailer import send_email_async, send_email_background
from models.user import User, User_Pydantic, UserIn_Pydantic, UserOut_Pydantic, Signup_Pydantic
from schemas.userSchema import Reset_Password_Schema, SignUpSchema
from datetime import datetime

settings = get_settings()

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/auth/login')

auth_handler = Auth()

JWT_SECRET = 'myjwtsecret'


async def authenticate_user(username: str, password: str):
    user = await User.filter(Q(username=username) | Q(email = username)).first()
    if not user:
        return False 
    if not user.verify_password(password):
        return False
    return user 

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    return await User_Pydantic.from_tortoise_orm(user)


@auth_router.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print('before auth')
    user = await authenticate_user(form_data.username, form_data.password)
    print('after auth', user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Please Verify your account!'
        )

    print(user, "user paydantinc 1")
    user_obj = await User_Pydantic.from_tortoise_orm(user)

    token = auth_handler.encode_token(user_obj.dict())
    refresh_token = auth_handler.encode_refresh_token(user_obj.dict())

    return { 'access_token' : token, 'token_type' : 'bearer', 'refresh_token': refresh_token }

@auth_router.post('/signup', response_model=UserOut_Pydantic)
async def create_user(user: SignUpSchema):
    if await User.get_or_none(email=user.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists"
        )

    if await User.get_or_none(username=user.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that username already exists"
        )


    user_obj = await User.create(
        email=user.email,
        username=user.username, 
        password=bcrypt.hash(user.password)
    )
    
    url = f'{settings.BASE_URL}/auth/verify-account/{auth_handler.get_confirmation_token(user_obj.username)}'
    print(url)

    email_object = {
        "subject": 'Account Activation',
        "email_to": user.email,
        "body": {
            'reset_url': url,
            'email': user.email,
            'username': user.username,
        },
    }
    await send_email_async(email_object, 'confirm-email')
    return await UserOut_Pydantic.from_tortoise_orm(user_obj)

@auth_router.get('/verify-account', )
async def account_activation(activationToken: str): 
    username = auth_handler.decode_token(activationToken)
    user = await User.get(username = username)
    user.is_verified = True
    user.is_activated = True
    user.email_verification_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    await user.save()

    return {
        'status': True,
        'message': 'User account activated successfully!',
    }

@auth_router.get('/users/me', response_model=User_Pydantic, response_model_exclude={"password"})
async def get_user(user: User_Pydantic = Depends(get_current_user)):
    return user

@auth_router.get('/refresh_token')
async def get_token(refresh_token: str):
    print(refresh_token)
    token = await auth_handler.refresh_token(refresh_token)
    return { 'token': token, 'refresh_token': refresh_token }

@auth_router.get('/users', response_model=List[UserOut_Pydantic])
async def get_users():
    users = await User.all()
    return users


@auth_router.get('/forgot-password')
async def forgot_password(email: str):
    user = await User.get_or_none(email = email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email does not exists"
        )
    
    confirmation = auth_handler.get_confirmation_token(user.username)
    url = f'{settings.BASE_URL}/auth/verify-reset-password/{confirmation}'
    print(url)

    emailObject = {
        "subject": 'Password Reset',
        "email_to": email,
        "body": {
            'reset_url': url,
            'email': email,
            'username': user.username,
        },
    }

    try:
        print('starting try')
        await send_email_async(emailObject, 'password-reset')

        return {
            "status": True,
            "Message": 'Email has been sent to your Inbox',
        } 

    except:
        status.HTTP_417_EXPECTATION_FAILED
        raise HTTPException(
            status_code= status.HTTP_417_EXPECTATION_FAILED,
            detail= {
                "status": False,
                "message": 'An error occurred.Please try again',
            }
        )


@auth_router.post('/reset-password')
async def reset_password( obj: Reset_Password_Schema):
    username = auth_handler.decode_token(obj.token)

    if obj.newPassword1 != obj.newPassword2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = {
                'status': False,
                'message': "Password are not the same."
            }
        )

    user = await User.get(username = username)

    user.password = bcrypt.hash(obj.newPassword1)
    await user.save()

    return {
        'status': True,
        'message': 'Password reset successfull!'
    }




