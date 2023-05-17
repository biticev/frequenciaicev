from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from config import db, create_app
from models import *
from sendfreq import run_script
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

main = Blueprint('main', __name__)

@main.route('/') # home page that return 'index'
def index():
    return render_template('index.html', )

@main.route('/relatorio') # profile page that return 'profile'
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

app = create_app() # we initialize our flask app using the            
                   #__init__.py function

scheduler = BackgroundScheduler(deamon=True)
scheduler.add_job(func=run_script, trigger="interval", minutes=60*24)
scheduler.start()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) # run the flask app on debug mode