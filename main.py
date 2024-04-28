import logging

from streamSchedule import create_app
from flask_apscheduler import APScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import request, redirect, url_for, render_template, abort, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import ConflictingIdError

from datetime import datetime, timedelta
from names import generate_name

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

app = create_app()
auth = HTTPBasicAuth()


if __name__ == "__main__":
    app.run(debug=True)


# jinja2 doesn't have easy date formatting
def format_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    """Format a datetime object to a string using strftime."""
    if value is None:
        return ""
    return value.strftime(format)


app.jinja_env.filters["datetime"] = format_datetime

# persist the schedule
# Broke recently :( maybe nested functions:
#app.config["SCHEDULER_JOBSTORES"] = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.db")}

# initialize scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

@auth.verify_password
def verify_password(username, password):
    authDict = app.config.get('AUTH', {})
    if username in authDict and check_password_hash(authDict[username], password):
        return username

# todo require auth
@app.route("/")
@auth.login_required
def nohit():
    abort(404)

# List current jobs
@app.route("/list")
@auth.login_required
def list():
    jobs = sorted(scheduler.get_jobs(), key=lambda x: x.next_run_time)
    return render_template("list.html.j2", jobs=jobs)


# todo require auth
@app.route("/add")
@auth.login_required
def add():
    return render_template("add.html.j2")


# todo require auth
@app.route("/submit", methods=["POST"])
@auth.login_required
def submit():
    # Get the name from the form
    logger.info(request.form)
    teamName = request.form.get("teamName")
    streamDate = request.form.get("date")
    streamTime = request.form.get("time")
    streamKey = request.form.get("streamKey")

    # Parse the date and time
    date_obj = datetime.strptime(streamDate, "%Y-%m-%d").date()
    time_obj = datetime.strptime(streamTime, "%H:%M").time()

    # Combine into a datetime object
    datetime_obj = datetime.combine(date_obj, time_obj)

    logger.info(f"NAME {teamName}")
    logger.info(f"DATE {streamDate}")
    logger.info(datetime_obj)
    new_stream(
        teamName,
        startTime=datetime_obj,
        duration=60 * 60 * 2.5,
        key=streamKey,
        config=app.config,
    )
    return redirect(url_for("list"))


def new_stream(name=False, startTime=False, duration=60 * 5, key="", config={}):
    now = datetime.now()

    if not name:
        name = generate_name()
    if not startTime:
        startTime = datetime(2025, 4, 14, 11, 50)

    endTime = startTime + timedelta(seconds=duration)

    # In Progress
    if startTime < now and endTime > now:
        startTime = now + timedelta(seconds=2)
        newDuration = endTime - now
        duration = newDuration.total_seconds()

    if not key:
        key = "sk_us-east-1_fakefake"

    try:
        scheduler.add_job(
            name,
            func="jobs:stream_game",
            kwargs={"duration": duration, "key": key, "config": config, "name": name},
            trigger=DateTrigger(run_date=startTime),
        )
    except ConflictingIdError:
        logger.info(f"Job '{name}' Already Seen")
        pass


# Backgroudn Job - Image Snapshots every 5m
now = datetime.now()
start_at_top_of_next_minute = now + timedelta(
    seconds=(60 - now.second), microseconds=(-now.microsecond)
)

scheduler.add_job(
    id="HIDDEN-Snapshots",
    name="Snapshot",
    func="jobs:snapshot",
    kwargs={
        "config": app.config,
    },
    trigger=IntervalTrigger(start_date=start_at_top_of_next_minute, minutes=5),
)
