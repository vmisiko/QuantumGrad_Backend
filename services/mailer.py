import os
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from dotenv import load_dotenv
load_dotenv('.env')


class Envs:
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME = os.getenv('MAIN_FROM_NAME')


conf = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    MAIL_DEBUG= True,
    SUPPRESS_SEND= False,
    TEMPLATE_FOLDER='./templates/email'
)


async def send_email_async(email_bject: dict, template: str):
    print(email_bject)
    message = MessageSchema(
        subject=email_bject['subject'],
        recipients=[email_bject['email_to']],
        template_body=email_bject['body'],
    )

    fm = FastMail(conf)

    await fm.send_message(message, template_name=f'{template}.html')


def send_email_background(background_tasks: BackgroundTasks, email_bject: dict, template: str):
    message = MessageSchema(
        subject=email_bject['subject'],
        recipients=[email_bject['email_to']],
        template_body=email_bject['body'],
    )

    fm = FastMail(conf)

    background_tasks.add_task(
        fm.send_message, message, template_name=f'{template}.html')

