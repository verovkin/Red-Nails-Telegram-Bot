import json
from pprint import pprint

import requests
from .services import WeatherService, WeatherServiceException





class User:
    def __init__(self, first_name, id, is_bot, language_code, username):
        self.first_name = first_name
        self.id = id
        self.is_bot = is_bot
        self.language_code = language_code
        self.username = username


class TelegramHandler:
    users = None

    def send_markup_message(self, text, markup):
        data = {
            'chat_id': self.user.id,
            'text': text,
            'reply_markup': markup,
        }
        requests.post(f'{TG_BASE_URL}{BOT_TOKEN}/sendMessage', json=data)


    def send_message(self, text):
        data = {
            'chat_id': self.user.id,
            'text': text,
        }
        requests.post(f'{TG_BASE_URL}{BOT_TOKEN}/sendMessage', json=data)



class MessageHandler(TelegramHandler):
    def __init__(self, data):
        self.user = User(**data.get('from'))
        self.text = data.get('text')

    def handle(self):
        match self.text.split():
            case WEATHER_TYPE, city:
                try:
                    geo_data = WeatherService.get_geo_data(city)
                    pprint(geo_data)
                except WeatherServiceException as wse:
                    self.send_message(str(wse))
                else:
                    buttons = []
                    for item in geo_data:
                        test_button = {
                            'text': f'{item.get("country")}, {item.get("name")}',
                            'callback_data': json.dumps(
                                {'type': WEATHER_TYPE, 'lat': item.get("latitude"), 'lon': item.get('longitude')}
                            ),
                        }
                        buttons.append([test_button])
                    markup = {
                        'inline_keyboard': buttons
                    }
                    self.send_markup_message('Choose a city', markup)


class CallbackHandler(TelegramHandler):

    def __init__(self, data):
        self.user = User(**data.get('from'))
        self.callback_data = json.loads(data.get('data'))

    def handle(self):
        callback_type = self.callback_data.pop('type')
        match callback_type:
            case WEATHER_TYPE:
                try:
                    weather = WeatherService.get_current_weatrher_by_geo_data(**self.callback_data)
                except WeatherServiceException as wse:
                    self.send_message(str(wse))
                else:
                    self.send_message(json.dumps(weather))