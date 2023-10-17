
from flask import Flask, render_template, request
from flask_apscheduler import APScheduler
import os
from threading import Thread
from gmail_service import GMailService
from openai_service import OpenaiAPI
import logging

from split_audio import SplitWavAudioMubin
from util import is_valid_email

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')

scheduler = APScheduler()
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        language = request.form['language']
        translation = 'translation' in request.form
        email = request.form['email']
        token = request.form['token']
        audio_file = request.files['audio']
        logging.info(f'here is a request. file_name:{audio_file.filename}, email: {email}, language: {language}')
        config_token = os.getenv('token')
        if token != config_token:
            return render_template('index.html', message='Please enter the correct token.')

        if not is_valid_email(email):
            return render_template('index.html', message='Please enter the correct email address.')

        if not audio_file:
            return render_template('index.html', message='Please upload the correct audio file.')

        audio_file.save(os.path.join('media', audio_file.filename))

        thread = Thread(target=go, args=(
            audio_file.filename, language, translation, email))
        thread.start()
        return render_template('index.html', message='Your audio file has been uploaded, pls check your email later')

    return render_template('index.html')


def go(file_name, language, translation, email):
    # split into small file
    split_wav = SplitWavAudioMubin('./media', file_name)
    split_wav.multiple_split(min_per_split=4)

    openai = OpenaiAPI('./media', file_name,
                       split_wav.split_files, language, translation)
    openai.speech2text()

    en_res = openai.texts
    zh_res = openai.translated_texts

    mail = GMailService(
        [email], f'[Speech2Text] {file_name}', en_res+zh_res)
    mail.send_email()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8089)
