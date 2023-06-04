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

    # def set_selected_procedure(self, selected_procedure):
    #     self.selected_procedure = selected_procedure
    #     print("selected procedure in user = ", self.selected_procedure)
    #
    # def set_selected_date(self, selected_date):
    #     self.selected_date = selected_date
    #     print("selected date in user = ", self.selected_date)
    #
    # def set_selected_time(self, selected_time):
    #     self.selected_time = selected_time
    #     print("selected time in user = ", self.selected_time)


class TelegramHandler:

    def split_buttons_on_rows(self, buttons_tmp, max_in_row):
        buttons = []
        button_row = []

        counter_in_row = 0
        while len(buttons_tmp) > 0:
            if counter_in_row < max_in_row:
                button_row.append(buttons_tmp.pop(0))
                counter_in_row += 1
                if len(buttons_tmp) == 0:
                    buttons.append(button_row)
            else:
                buttons.append(button_row)
                button_row = []
                counter_in_row = 0
        return buttons

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
                        's': 'menu',
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
                self.show_start_menu()
                # self.send_message(Messages.DEFAULT)


class CallbackHandler(TelegramHandler):
    def __init__(self, data):
        self.user = User(**data.get('from'))
        self.callback_data = json.loads(data.get("data"))

        # self.selected_date = 'not set'
        # self.selected_time = 'not set'
        # self.selected_procedure = 'not set'

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
        print("==showing procedures")
        buttons = []
        procedures = db.session.query(Procedure).all()

        for procedure in procedures:
            procedure_button = {
                'text': f'{procedure.name} ({procedure.duration_minutes}min) - {procedure.price}UAH',
                'callback_data': json.dumps(
                    {
                        's': 'p',
                        'p': procedure.id
                    }
                ),
            }
            buttons.append([procedure_button])

        back_button = {
            'text': 'Go back',
            'callback_data': json.dumps(
                {
                    's': "back",
                    'b': 'start',
                 }
            ),
        }
        buttons.append([back_button])
        markup = {
            'inline_keyboard': buttons
        }
        self.send_markup_message(Messages.CHOOSE_PROCEDURE, markup)

    def show_available_days(self, selected_procedure):
        buttons_tmp = []

        for i in range(WorkingSetting.SHOW_NUMBER_OF_DAYS):

            the_date = date.today() + timedelta(days=i)
            the_date_str = the_date.strftime("%Y-%m-%d")
            date_to_show = the_date.strftime("%a, %d %b")

            date_button = {
                'text': date_to_show,
                'callback_data': json.dumps(
                    {
                        's': 'd',
                        'p': selected_procedure,
                        'd': the_date_str,
                    }
                ),
            }
            buttons_tmp.append(date_button)

        back_button = {
            'text': 'Go back',
            'callback_data': json.dumps(
                {
                    's': 'back',
                    'b': 'p',
                    'p': selected_procedure
                }
            ),
        }
        buttons_tmp.append(back_button)

        markup = {'inline_keyboard': self.split_buttons_on_rows(buttons_tmp, 3)}
        self.send_markup_message(Messages.CHOOSE_DAY, markup)

    def show_available_time(self, selected_procedure, selected_date):
        # self.selected_time = None
        print("show times")
        # procedure_duration = db.session.query(Procedure.duration_minutes).filter_by(id=self.user.selected_procedure).one()[0]

        day_start = selected_date.replace(hour=WorkingSetting.WORKING_HOUR_START)
        print("selected day = ", day_start)
        day_end = selected_date.replace(hour=WorkingSetting.WORKING_HOUR_END)
        time_delta = timedelta(minutes=30)

        date_str = day_start.strftime("%Y-%m-%d")

        buttons_tmp = []

        while day_start < day_end:

            time_txt = day_start.strftime("%-H:%M")
            time_str = day_start.strftime("%H:%M")


            time_button = {
                'text': time_txt,
                'callback_data': json.dumps(
                    {
                        's': 't',
                        'd': date_str,
                        't': time_str,
                        'p': selected_procedure,
                    }
                ),
            }
            day_start += time_delta
            buttons_tmp.append(time_button)

        back_button = {
            'text': 'Go back',
            'callback_data': json.dumps(
                {
                    's': "back",
                    'b': "d",
                    'd': date_str,
                    'p': selected_procedure,
                }
            ),
        }
        buttons_tmp.append(back_button)

        markup = {'inline_keyboard': self.split_buttons_on_rows(buttons_tmp, 3)}
        self.send_markup_message(Messages.CHOOSE_TIME, markup)


    def show_confirm(self, selected_procedure, selected_date, selected_time):
        print("in confirm")

        procedure = db.session.query(Procedure).filter_by(id=selected_procedure).all()
        pprint(procedure)
        selected_date_str = selected_date.strftime("%a, %d %b")
        message = f"You are booking a <b>{procedure[0].name}</b> for <b>{procedure[0].price}UAH</b>, on <b>{selected_date_str}</b> at <b>{selected_time}</b>"

        date_str = selected_date.strftime("%Y-%m-%d")

        buttons = [
            [{
                'text': 'YES',
                'callback_data': json.dumps({
                    's': 'y',
                    'p': selected_procedure,
                    'd': date_str,
                    't': selected_time
                })
            },
            {
                'text': 'NO',
                'callback_data': json.dumps({
                    's': 'back',
                    'b': 't',
                    'd': date_str,
                    'p': selected_procedure
                })
            },
            ]]

        markup = {'inline_keyboard': buttons}
        self.send_markup_message(message, markup)
        print("ok")

    def save_record_to_db(self, selected_procedure, selected_date, selected_time):
        print("IN CONFIRM")
        print("sel date = ", selected_date)
        print("date time = ", selected_time)
        print("pprocedure id =", selected_procedure)
        # new_record = Record(client_id=self.user.id, )
        pprint(self.user)
        self.send_message(Messages.CONFIRMED)


    def handle(self):
        match self.callback_data.get("s"):
            # button BACK
            case 'back':
                match self.callback_data.get("b"):
                    case 'start':
                        self.show_start_menu()
                    case 'p':  # PROCEDURE SELECT
                        self.show_procedure_list()
                    case 'd':  # DATE SELECT
                        selected_procedure = self.callback_data.get("p")
                        self.show_available_days(selected_procedure)
                    case 't':  # TIME SELECT
                        selected_procedure = self.callback_data.get("p")
                        selected_date = datetime.strptime(self.callback_data.get("d"), '%Y-%m-%d')
                        self.show_available_time(selected_procedure, selected_date)

            # buttons in MAIN MENU
            case 'menu':
                match self.callback_data.get("id"):
                    case '/procedure_list':
                        print("main_menu")
                        self.show_procedure_list()
                    case '/planned_visit':
                        print("main_menu")
                        self.show_records()
                    case '/address':
                        print("main_menu")
                        self.show_how_to_get_us()
                    case '/about':
                        print("main_menu")
                        self.show_about_us()

            case 'p':  # SELECTED PROCEDURE
                selected_procedure = self.callback_data.get("p")
                print("IN P - sel procedure")
                print("selected procedure", selected_procedure)
                self.show_available_days(selected_procedure)

            case 'd':  # SELECTED DAY
                selected_procedure = self.callback_data.get("p")
                selected_date = datetime.strptime(self.callback_data.get("d"), '%Y-%m-%d')
                print("IN D - sel day")
                print("selected procedure", selected_procedure)
                print("selected date ", selected_date)
                self.show_available_time(selected_procedure, selected_date)

            case 't':  # SELECTED TIME
                selected_procedure = self.callback_data.get("p")
                selected_date = datetime.strptime(self.callback_data.get("d"), '%Y-%m-%d')
                selected_time = self.callback_data.get("t")
                print("IN T - sel time")
                print("selected procedure", selected_procedure)
                print("selected date ", selected_date)
                print("selected time = ", selected_time)
                self.show_confirm(selected_procedure, selected_date, selected_time)

            case 'y':  # CONFIRMED
                selected_procedure = self.callback_data.get("p")
                # selected_date = datetime.strptime(self.callback_data.get("d"), '%Y-%m-%d')
                selected_date = self.callback_data.get("d")
                selected_time = self.callback_data.get("t")

                print("in Y - SAID YES CONFIRMED TIME TO SAVE TO DB")
                print("time", selected_time)
                print("date = ", selected_date)
                print("pprocedure id =", selected_procedure)

                # new_record = Record(client_id=self.user.id, )
                self.send_message("OK")
                # self.save_record_to_db()
