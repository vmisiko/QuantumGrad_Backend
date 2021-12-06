import jwt
from fastapi import Depends, HTTPException
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from pydantic import UUID4
from pydantic.types import conset
from starlette.types import Message
from models.user import User, User_Pydantic


JWT_SECRET = 'myjwtsecret'


class Auth():

    def encode_token(self, user):
        payload = {
            'exp' : (datetime.utcnow() + timedelta(days=0, minutes=30)),
            'iat' : datetime.utcnow(),
        }

        
        if 'created_at' in user:
            user.pop('created_at')
            user.pop('email_verification_date')
        
        payload.update(user)

        return jwt.encode(
            payload, 
            JWT_SECRET,
            algorithm='HS256'
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            print(payload)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401, 
                detail= {
                    "status": False,
                    "message": 'Token has expired'
                }
            )
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail= {
                    "status": False,
                    "message": 'invalid Token'
                })

    def encode_refresh_token(self, user):
            print(user['username'], 'encode_refresh_token')
            payload = {
                'exp' : datetime.utcnow() + timedelta(days=0, hours=10),
                'iat' : datetime.utcnow(),
                'scope': 'refresh_token',
                'sub' : user['username'],
            }

            return jwt.encode(
                payload, 
                JWT_SECRET,
                algorithm='HS256'
            )

    async def refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=['HS256'])
            print(payload)
            if (payload['scope'] == 'refresh_token'):
                username = payload['sub']
                user = await User.get(username=username)
                user_obj = await User_Pydantic.from_tortoise_orm(user)
                new_token = self.encode_token(user_obj.dict())
                return new_token
            raise HTTPException(status_code=401, detail='Invalid scope for token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Refresh token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid refresh token')
   
    def get_confirmation_token(self, username):
        payload = {
            'exp' : datetime.utcnow() + timedelta(days=0, hours=10),
            'iat' : datetime.utcnow(),
            'scope': 'registration',
            'sub' : str(username),
        }
        
        print(payload, 'payload in get_confirmation_token')
        token = self.encode_token(payload)
        
        print(self.decode_token(token), 'decoded token')
        return token
    
