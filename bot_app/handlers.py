import datetime
import json
from pprint import pprint
from flask import request
import requests
from bot_app import app, db
from .config import Messages, AppConfig, select_options, WorkingSetting
from .models import *
from datetime import date, timedelta, datetime
import time
# import emoji


BOT_TOKEN = app.config.get('BOT_TOKEN')
TG_URL = 'https://api.telegram.org/bot' + BOT_TOKEN


class User:
    def __init__(self, first_name, id, is_bot, language_code, username):
        self.name = first_name
        self.chat_id = id
        self.is_bot = is_bot
        self.language_code = language_code
        self.username = username
        self.selected_date = None
        self.selected_time = None
        self.selected_procedure = None



class TelegramHandler:

    def send_markup_message(self, text, markup):
        data = {
            'chat_id': self.user.chat_id,
            'text': text,
            'reply_markup': markup,
            'parse_mode': 'HTML',
        }
        requests.post(f'{TG_URL}/sendMessage', json=data)

    def send_message(self, text):
        data = {
            'chat_id': self.user.chat_id,
            'text': text,
            'parse_mode': 'HTML',
        }
        requests.post(f'{TG_URL}/sendMessage', json=data)

    def send_hello_message(self):
        self.send_message(Messages.WELCOME)

    def show_start_menu(self):
        buttons = []

        for option in select_options:
            menu_button = {
                'text': option.get('name'),
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


    def show_how_to_get_us(self):
        buttons = []
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
                    'back_to': 'start',
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
        buttons = []
        back_button = {
            'text': 'Go back',
            'callback_data': json.dumps(
                {
                    'type': "back",
                    'back_to': 'start',
                }
            ),
        }
        buttons.append([back_button])
        markup = {
            'inline_keyboard': buttons
        }
        self.send_markup_message(Messages.ABOUT_US, markup)

    def show_records(self):
        client_records = db.session.query(Record, Client, Procedure).join(Client).join(Procedure).filter(Client.tg_id == self.user.chat_id).all()

        # if no client records
        if len(client_records) < 1:
            buttons = []
            back_button = {
                'text': 'Go back',
                'callback_data': json.dumps(
                    {
                        'type': "back",
                        'back_to': 'start',
                    }
                ),
            }
            buttons.append([back_button])
            markup = {
                'inline_keyboard': buttons
            }
            self.send_markup_message(Messages.NON_SCHEDULED, markup)

        # if records exists
        else:
            pass
            # for client_record in client_records:
            #     buttons = []
            #     client_record_button = {
            #         'text': f'{client_record.pro} ({procedure.duration_minutes}min) - {procedure.price}UAH',
            #         'callback_data': json.dumps(
            #             {
            #                 'type': 'procedure',
            #                 'id': procedure.id
            #             }
            #         ),
            #     }
            #         buttons.append([procedure_button])
            #
            #     back_button = {
            #         'text': 'Go back',
            #         'callback_data': json.dumps(
            #             {
            #                 'type': "back",
            #                 'id': 1,
            #             }
            #         ),
            #     }
            #     buttons.append([back_button])
            #     markup = {
            #         'inline_keyboard': buttons
            #     }
            #
            #     self.send_markup_message(Messages.CHOOSE_PROCEDURE, markup)

    def show_procedure_list(self):

        print("==show procedures")
        buttons = []
        procedures = db.session.query(Procedure).all()

        for procedure in procedures:
            procedure_button = {
                'text': f'{procedure.name} ({procedure.duration_minutes}min) - {procedure.price}UAH',
                'callback_data': json.dumps(
                    {
                        'type': 'sel_procedure',
                        'procedure_id': procedure.id
                    }
                ),
            }
            buttons.append([procedure_button])

        back_button = {
            'text': 'Go back',
            'callback_data': json.dumps(
                {
                    'type': "back",
                    'back_to': 'start',
                 }
            ),
        }
        buttons.append([back_button])
        markup = {
            'inline_keyboard': buttons
        }
        self.send_markup_message(Messages.CHOOSE_PROCEDURE, markup)

    def show_available_days(self, procedure_id):
        print("show days")

        buttons = []

        for i in range(WorkingSetting.SHOW_NUMBER_OF_DAYS):

            the_date = date.today() + timedelta(days=i)
            date_to_show = the_date.strftime("%a, %d %b")
            the_date_str = str(the_date)

            date_button = {
                'text': date_to_show,
                'callback_data': json.dumps(
                    {
                        'type': 'sel_date',
                        'date': the_date_str,
                        'procedure_id': procedure_id
                    }
                ),
            }
            buttons.append([date_button])

        back_button = {
            'text': 'Go back',
            'callback_data': json.dumps(
                {
                    'type': 'back',
                    'back_to': 'procedures'
                }
            ),
        }
        buttons.append([back_button])

        markup = {'inline_keyboard': buttons}
        self.send_markup_message(Messages.CHOOSE_DAY, markup)

    def show_available_time(self, the_date, procedure_id):
        print("show times")
        procedure_duration = db.session.query(Procedure.duration_minutes).filter_by(id=procedure_id).one()[0]

        day_start = datetime.strptime(the_date, '%Y-%m-%d').replace(hour=WorkingSetting.WORKING_HOUR_START)
        day_end = datetime.strptime(the_date, '%Y-%m-%d').replace(hour=WorkingSetting.WORKING_HOUR_END)
        time_delta = timedelta(minutes=30)

        buttons = []

        while day_start < day_end:
            day_start += time_delta

            time_txt = day_start.strftime("%h:%M")
            print(day_start, time_txt)

            time_button = {
                'text': time_txt,
                'callback_data': json.dumps(
                    {
                        'type': 'sel_time',
                        'datetime': str(day_start),
                        'pr_id': procedure_id,
                    }
                ),
            }
            buttons.append([time_button])

        back_button = {
            'text': 'Go back',
            'callback_data': json.dumps(
                {
                    'type': "back",
                    'back_to': "date",
                }
            ),
        }
        buttons.append([back_button])
        markup = {'inline_keyboard': buttons}
        self.send_markup_message(Messages.CHOOSE_TIME, markup)


    def show_confirm(self, procedure_id, selected_datetime):

        text = f"You are booking a"   #TODO name of procedure add
        self.send_message(text)

        buttons = []

        confirmation_button = [
            {
                'text': 'YES',
                'callback_data': json.dumps(
                    {
                        'type': 'confirm',
                        'datetime': selected_datetime,
                        'procedure_id': procedure_id,
                    }
                ),
            },
            {
                'text': 'NO',
                'callback_data': json.dumps(
                    {
                        'type': 'back',
                        'back_to': 'start',
                    }
                ),
            },
        ]

        buttons.append([confirmation_button])


    def save_record_to_db(self, selected_datetime, procedure_id):
        print("date time = ", selected_datetime)
        print("pprocedure id =", procedure_id)
        # new_record = Record(client_id=self.user.id, )
        self.send_message(Messages.CONFIRMED)



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
            case '/address':
                self.show_how_to_get_us()
            case '/about':
                self.show_about_us()
            case _:
                self.send_message(Messages.DEFAULT)


class CallbackHandler(TelegramHandler):
    def __init__(self, data):
        self.user = User(**data.get('from'))
        self.callback_data = json.loads(data.get("data"))

    def handle(self):
        match self.callback_data.get("type"):
            # button BACK
            case 'back':
                match self.callback_data.get("back_to"):
                    case 'start':
                        self.show_start_menu()
                    case 'procedures':
                        self.show_procedure_list()
                    case 'date':
                        self.show_available_days()

            # buttons in MAIN MENU
            case 'menu':
                match self.callback_data.get("id"):
                    case 'procedure_list':
                        self.show_procedure_list()
                    case 'planned_visit':
                        self.show_records()
                    case '/address':
                        self.show_how_to_get_us()
                    case '/about':
                        self.show_about_us()

            case 'sel_procedure':       # client has selected procedure
                print(389)
                procedure_id = self.callback_data.get("procedure_id")
                self.show_available_days(procedure_id)

            case 'sel_date':
                selected_date = self.callback_data.get("date")
                procedure_id = self.callback_data.get("procedure_id")
                self.show_available_time(selected_date, procedure_id)

            case 'sel_time':
                procedure_id = self.callback_data.get("pr_id")
                selected_datetime = self.callback_data.get("datetime")
                print(f"procedure {procedure_id} at {selected_datetime}")
                self.show_confirm(procedure_id, selected_datetime)

            case 'confirm':
                procedure_id = self.callback_data.get("procedure_id")
                selected_datetime = self.callback_data.get("datetime")
                self.save_record_to_db(selected_datetime, procedure_id)


