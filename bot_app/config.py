import os
from dotenv import load_dotenv
import datetime

load_dotenv()


class AppConfig:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    BOT_TOKEN = os.getenv('BOT_TOKEN')


class Messages:
    WELCOME = 'Hi and welcome, to our <b>Red Nail Studio!<b>'
    CHOICE = 'Please make your choice:'
    CHOOSE_PROCEDURE = 'Choose procedure:'
    ADDRESS_TEXT = "<b>You can find us here:</b>\n<i>Red Nail Studio, 37 The Green, Aberdeen AB11 6NY, UK</i>"
    ADDRESS_FOR_URL = "https://goo.gl/maps/RZAHjuneLTZHrr1F7"
    ABOUT_US = 'We are the best <b>Nail Studio</b> in the Universe, we can do simultaneously not only right hand, but also left hand!'
    SCHEDULED = 'We are waiting for you '
    NON_SCHEDULED = "You have no scheduled visits yet."
    CHOOSE_DAY = "Available days:"
    CHOOSE_TIME = "Available time:"
    DEFAULT = "Sorry, I don't understand you, please try again."
    CONFIRMED = "Your visit booked!"


select_options = [
    {'id': 'procedure_list', 'type': 'menu', 'name': 'Procedure List'},
    {'id': 'planned_visit', 'type': 'menu', 'name': 'Your planned visit'},
    {'id': '/address', 'type': 'menu', 'name': 'How to get us'},
    {'id': '/about', 'type': 'menu', 'name': 'About us'},
]


class WorkingSetting:
    WORKING_HOUR_START = 10
    WORKING_HOUR_END = 15
    SHOW_NUMBER_OF_DAYS = 7
