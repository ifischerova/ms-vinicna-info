from flask import Flask, flash, render_template, redirect, url_for, request, session
from flask_wtf.csrf import CSRFProtect, CSRFError
from dotenv import load_dotenv
import os
import requests
from flask_recaptcha import ReCaptcha

from app.send_emails import send_activation_email

# Load environment variables from .env file.
load_dotenv()

app = Flask(__name__)
app.secret_key = 'rbYPVS3hLzIToOJ'
app.templates_auto_reload = True

if app.debug == False:
    app.config['RECAPTCHA_SITE_KEY'] = os.environ.get('RECAPTCHA_SITE_KEY') 
    app.config['RECAPTCHA_SECRET_KEY'] = os.environ.get('RECAPTCHA_SECRET_KEY') 
    recaptcha = ReCaptcha(app) # Create a ReCaptcha object by passing in 'app' as parameter

csrf = CSRFProtect(app)
csrf.init_app(app)

worker_url = os.environ.get('WORKER_URL')

@app.route('/')
def get_main_page():
    email_address = session.pop('email_address', '')
    # I need to specify the debug mode for the template "to know" about this mode.   
    return render_template('index.html', email_address=email_address, debug=app.debug)

@app.route('/unsubscribe', methods=['GET'])
def get_unsubscribe_page():
    email_address = session.pop('email_address', '')
    return render_template('unsubscribe.html', email_address=email_address, debug=app.debug)

@app.route('/', methods=['POST'])
def submit_new_email():
    email_address = request.form['input_email'] 

    if email_address == '':
        flash('Vyplňte prosím emailovou adresu.', 'error')
        session['email_address'] = email_address
        return redirect(url_for('get_main_page'))
    
    if '@' not in email_address :
        flash('Emailová adresa nemá správný formát.', 'error')
        session['email_address'] = email_address
        return redirect(url_for('get_main_page'))

    if app.debug == False:
        if not recaptcha.verify(): # Use verify() method to see if ReCaptcha is filled out
            flash('Potvrďte prosím, že nejste robot.', 'error')
            session['email_address'] = email_address
            return redirect(url_for('get_main_page'))

    r = requests.put(worker_url + '/activation', json={ "email": email_address }, headers={ 'X-Auth-Token': os.environ.get('WORKER_AUTH_TOKEN')})
    if r.status_code == 409:
        flash('Tento email je již přihlášen.', 'error')
        return redirect(url_for('get_main_page'))

    token = r.json().get('token', None)

    if not token:
        flash('Registrace se nezdařila, zkuste opakovat akci.', 'error')
        session['email_address'] = email_address
        return redirect(url_for('get_main_page'))

    send_activation_email(email_address, token, debug=app.debug)

    session.pop('email_address', None)
    return redirect(url_for('show_thank_you_landing_page'))

@app.route('/thank_you')
def show_thank_you_landing_page():
    return render_template('thank_you_lp.html')

@app.route('/gdpr')
def show_gdpr_page():
    return render_template('gdpr.html')

@app.route('/activation/<string:token>')
def activate_email(token):
    r = requests.post(worker_url + '/activation', json={ 'token': token }, headers={ 'X-Auth-Token': os.environ.get('WORKER_AUTH_TOKEN')})
    
    if r.status_code == 409:
        flash('Tenhle email je již aktivován.', 'error')
    elif r.status_code == 404:
        flash('Platnost linku vypršela.', 'error')
    elif r.status_code == 200:
        flash('Email byl úspěšně aktivován.', 'success')
    else:
        flash('Neočekávaná chyba, zkuste to prosím později.', 'error')
    return redirect(url_for('get_main_page'))

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe_email():
    email_address = request.form['input_email']
    if email_address == '':
        flash('Vyplňte prosím emailovou adresu.', 'error')
        session['email_address'] = email_address
        return redirect(url_for('get_unsubscribe_page'))
    
    if '@' not in email_address :
        flash('Emailová adresa nemá správný formát.', 'error')
        session['email_address'] = email_address
        return redirect(url_for('get_unsubscribe_page'))

    if app.debug == False: 
        if not recaptcha.verify(): # Use verify() method to see if ReCaptcha is filled out
            flash('Potvrďte prosím, že nejste robot.', 'error')
            session['email_address'] = email_address
            return redirect(url_for('get_unsubscribe_page'))

    r = requests.delete(worker_url + '/email', json={ "email": email_address }, headers={ 'X-Auth-Token': os.environ.get('WORKER_AUTH_TOKEN')})

    if r.status_code == 404:
        flash('Odběr článků nejde zrušit - emailová adresa není registrována.', 'error')
        session['email_address'] = email_address
    elif r.status_code == 204:
        flash('Odběr článků je zrušen.', 'success')
    else:
        flash('Nastala neočekávaná chyba, zkuste to prosím později.', 'error')

    return redirect(url_for('get_unsubscribe_page'))

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash(f'{ e.description }', 'error')
    return redirect(url_for('get_main_page'))

@app.before_request
def check_csrf():
    csrf.protect()

if __name__ == '__main__':
    app.run()