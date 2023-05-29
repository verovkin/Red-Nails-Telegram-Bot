from pprint import pprint

import requests

from bot_app import app, db
from flask import request, jsonify, render_template

from .models import *

# from .handlers import MessageHandler, CallbackHandler


BOT_TOKEN = app.config.get('BOT_TOKEN')
TG_BASE_URL = 'https://api.telegram.org/bot' + BOT_TOKEN + '/'


@app.route('/', methods=["POST", "GET"])
def handler():
    chat_id = request.json.get('message').get('chat').get('id')
    name = request.json.get('message').get('chat').get('first_name')

    # check if it's a new client
    purchase = db.session.query(Client).filter(Client.tg_id == chat_id).all()
    if len(purchase) < 1:
        # add a new client to DB
        client = Client(tg_id=chat_id, name=name)
        db.session.add(client)
        db.session.commit()
        print(f"Client id={chat_id} {name} added")

    return 'ok'


@app.route('/list')
def list():
    procedures = db.session.query(Procedure).all()

    return str(len(procedures))


@app.route('/clients')
def clients_list():
    clients = db.session.query(Client).all()
    return render_template('clients.j2', clients=clients)


@app.route('/procedures')
def procedures_list():
    procedures = db.session.query(Procedure).all()
    return render_template('procedures.j2', procedures=procedures)

