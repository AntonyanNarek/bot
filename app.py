import asyncio

from datetime import datetime

from flask import Flask, render_template, jsonify

from database import logger_app

app = Flask(__name__, static_folder='static')

@app.route('/')
async def hello():
    logs = await logger_app.select()
    filter_id = list(set(log[4] for log in logs))
    return render_template('index.html', logs=reversed(logs), filter_id=filter_id, version=datetime.now().timestamp())


@app.route('/logging_log')
async def show_log_file():
    log_filename = '/root/project/project.err.log'

    try:
        with open(log_filename, 'r', encoding='utf-8', errors='ignore') as log_file:
            log_content = log_file.read()
    except FileNotFoundError:
        log_content = 'Файл не найден'

    return render_template('log.html', log_content=log_content)


@app.route('/logs')
async def get_logs():
    logs = await logger_app.select()
    filter_id = list(set(log[4] for log in logs))
    return jsonify(logs=list(reversed(logs)), filter_id=filter_id)


if __name__ == '__main__':
    app.run()
