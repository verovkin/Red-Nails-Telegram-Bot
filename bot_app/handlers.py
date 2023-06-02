
import json
from pprint import pprint
from flask import request
import requests
from bot_app import app, db
from .config import Messages, AppConfig, select_options
from .models import *


BOT_TOKEN = app.config.get('BOT_TOKEN')
TG_URL = 'https://api.telegram.org/bot' + BOT_TOKEN



class User:
    def __init__(self, first_name, id, is_bot, language_code, username):
        self.name = first_name
        self.chat_id = id
        self.is_bot = is_bot
        self.language_code = language_code
        self.username = username




class TelegramHandler:
    # users = None

    def send_markup_message(self, text, markup):
        data = {
            'chat_id': self.user.chat_id,
            'text': text,
            'reply_markup': markup,
        }
        requests.post(f'{TG_URL}/sendMessage', json=data)


    def send_message(self, text):
        data = {
            'chat_id': self.user.chat_id,
            'text': text,
        }
        requests.post(f'{TG_URL}/sendMessage', json=data)


    def send_hello_message(self):
        self.send_message(Messages.WELCOME)

    def show_start_menu(self):
        buttons = []

        for option in select_options:
            menu_button = {
                'text': f"{option.get('id')} - {option.get('name')}",
                'callback_data': json.dumps(
                    {
                        'type': 'menu',
                        'id': option.get('id'),
                    }
                ),
            }
            buttons.append([menu_button])
        markup = {
            'inline_keyboard': buttons
        }
        self.send_markup_message(Messages.CHOICE, markup)





    def show_procedure_list(self):
        buttons = []
        procedures = db.session.query(Procedure).all()

        for procedure in procedures:
            procedure_button = {
                'text': f'{procedure.name} ({procedure.duration_minutes}min) - {procedure.price}UAH',
                'callback_data': json.dumps(
                    {
                        'type': 'procedure',
                        'id': procedure.id
                    }
                ),
            }
            buttons.append([procedure_button])

        back_button = {
            'text': 'Go back',
            'callback_data': json.dumps(
                {
                    'type': "back",
                    'id': 1,
                 }
            ),
        }
        buttons.append([back_button])
        markup = {
            'inline_keyboard': buttons
        }

        self.send_markup_message(Messages.CHOOSE_PROCEDURE, markup)


    def show_how_to_get_us(self):
        buttons = []
        #
        menu_button = {
            'text': "Show in Google Maps",
            'url': Messages.ADDRESS_FOR_URL,
        }
        buttons.append([menu_button])
        back_button = {
            'text': 'Go back',
            'callback_data': json.dumps(
                {
                    'type': "back",
                    'id': 1,    # back to level 1
                }
            ),
        }
        buttons.append([back_button])
        markup = {
            'inline_keyboard': buttons
        }
        self.send_markup_message(Messages.ADDRESS_TEXT, markup)



        # procedures = db.session.query(Procedure).all()
        #
        # for procedure in procedures:
        #     procedure_button = {
        #         'text': f'{procedure.name} ({procedure.duration_minutes}min) - {procedure.price}UAH',
        #         'callback_data': json.dumps(
        #             {'procedure_id': procedure.id}
        #         ),
        #     }
        #     buttons.append([procedure_button])
        # markup = {
        #     'inline_keyboard': buttons
        # }
        #
        # self.send_markup_message(Messages.CHOOSE_PROCEDURE, markup)





    def show_about_us(self):
        self.send_message(Messages.ABOUT_US)




class MessageHandler(TelegramHandler):
    def __init__(self, data):
        self.user = User(**data.get('from'))
        self.text = data.get('text')
        self.check_user_exist()

    def check_user_exist(self):
        # check if user_id is in DB
        client_list_with_id = db.session.query(Client).filter(Client.tg_id == self.user.chat_id).all()
        if len(client_list_with_id) < 1:
            # add a new client to DB
            client = Client(tg_id=self.user.chat_id, name=self.user.name)
            db.session.add(client)
            db.session.commit()
            self.send_hello_message()






    def handle(self):

        match self.text:
            case '/start':
                self.show_start_menu()
            case '/procedures':
                self.show_procedure_list()
            case _:
                self.send_message(Messages.DEFAULT)



class CallbackHandler(TelegramHandler):
    def __init__(self, data):
        self.user = User(**data.get('from'))
        self.callback_data = json.loads(data.get("data"))


    def handle(self):
        match self.callback_data.get("type"):
            case 'back':
                self.show_start_menu()

            case 'menu':
                match self.callback_data.get("id"):
                    case 1:
                        self.show_procedure_list()
                    case 2:
                        pass
                    case 3:
                        self.show_how_to_get_us()
                    case 4:
                        self.show_about_us()

            case 'procedure':
                match self.callback_data.get("id"):
                    case 1:
                        pass
                    case 2:
                        pass

