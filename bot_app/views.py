from pprint import pprint

import werkzeug.exceptions

from bot_app import app, db
from flask import request, jsonify, render_template

from .models import *

from .handlers import MessageHandler, CallbackHandler





@app.route('/')
def index():
    return render_template('main.j2')


@app.post('/')
def handler():
    if message := request.json.get('message'):
        handler = MessageHandler(message)
    elif callback := request.json.get('callback_query'):
        handler = CallbackHandler(callback)

    handler.handle()
    return 'ok'


@app.route('/clients')
def clients_list():
    clients = db.session.query(Client).all()
    return render_template('clients.j2', clients=clients)


@app.route('/records')
def records_list():
    records = db.session.query(Record, Client, Procedure).join(Client).join(Procedure).all()
    return render_template('records.j2', records=records)




@app.route('/procedures')
def procedures_list():
    procedures = db.session.query(Procedure).all()
    return render_template('procedures.j2', procedures=procedures)


@app.errorhandler(werkzeug.exceptions.NotFound)
def default_404(e):
    return render_template('404.j2'), 404