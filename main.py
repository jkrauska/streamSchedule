import logging

from streamSchedule import create_app
from flask_apscheduler import APScheduler
from flask import session, request, redirect, url_for, render_template

from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.base import ConflictingIdError

from datetime import datetime
from names import generate_name

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)


# jinja2 doesn't have easy date formatting
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object to a string using strftime."""
    if value is None:
        return ""
    return value.strftime(format)
app.jinja_env.filters['datetime'] = format_datetime


# persist the schedule
#app.config["SCHEDULER_JOBSTORES"] = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.db")}

# initialize scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# List current jobs
# todo require auth
@app.route("/list")
def list():
    jobs = sorted(scheduler.get_jobs(), key=lambda x: x.next_run_time)
    return render_template('list.html.j2', jobs=jobs)

# todo require auth
@app.route("/add")
def add():
    return render_template('add.html.j2')

# todo require auth
@app.route('/submit', methods=['POST'])
def submit():
    # Get the name from the form
    teamName = request.form['teamName']
    date = request.form['date']
    new_stream(scheduler, name=teamName)
    return redirect(url_for('list'))


def new_stream(name=False, startTime=False, duration=60*5, key="", config={}):
    if not name:
        name = generate_name()
    if not startTime:
        startTime = datetime(2025, 4, 14, 11, 50)
    if not key:
        key = "sk_us-east-1_fakefake"

    try:
        scheduler.add_job(
            name,
            func="jobs:stream_game",
            kwargs={
                "duration": duration,
                "key": key,
                "config": config
                },       
                trigger=DateTrigger(run_date=startTime)     
        )
    except ConflictingIdError:
        logger.info(f"Job '{name}' Already Seen")
        pass    


new_stream()
new_stream("Cubs", 
           startTime=datetime.now(), 
           duration=60*60*2.5,
           key='sk_us-east-1_UwwoLJyfc2Fe_CnZKAOSieknUY5DXaYT1vV?gc_ext=true',
           config=app.config)