import os
from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    BOT_TOKEN = os.getenv('BOT_TOKEN')


class Messages:
    WELCOME = 'Hi and welcome, to our Red Nail Studio!'
    CHOICE = 'Please make your choice:'
    CHOOSE_PROCEDURE = 'Choose procedure:'
    ADDRESS_TEXT = "You can find us here:\nRed Nail Studio, 37 The Green, Aberdeen AB11 6NY, UK"
    ADDRESS_FOR_URL = "https://goo.gl/maps/RZAHjuneLTZHrr1F7"
    ABOUT_US = 'We are the best Nail Studio in the Universe, we can do simultaneously not only right hand, but also left hand!'
    DEFAULT = "Sorry, I don't understand you, please try again."


select_options = [
    {'id': 1, 'type': 'menu', 'name': 'Procedure List'},
    {'id': 2, 'type': 'menu', 'name': 'Your planned visit'},
    {'id': 3, 'type': 'menu', 'name': 'How to get us'},
    {'id': 4, 'type': 'menu', 'name': 'About us'},
]

