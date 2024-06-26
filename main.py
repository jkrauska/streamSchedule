import json
import logging
import subprocess
from datetime import datetime, timedelta

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import abort, redirect, render_template, request, url_for
from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import Bcrypt

from werkzeug.security import check_password_hash

from names import generate_name
from streamSchedule import create_app

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# logging.getLogger('apscheduler').setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


# Read config from file
with open("secrets.json", "r") as file:
    SECRETS = json.load(file)


app = create_app()
bcrypt = Bcrypt(app)

auth = HTTPBasicAuth()
process_dict = {}


# Define a function to run a subprocess in Bash
def run_bash_command(cmd):

    logging.info(f"Starting {cmd}")

    try:
        subprocess.run(cmd, check=True, shell=True)
        logging.info("Exited")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error: {e}")


def stop_subprocess(job_id):
    # Retrieve the process handle
    proc = process_dict.get(job_id)
    if proc:
        # Terminate the process
        proc.terminate()
        print(f"Stopped job {job_id}")
        # Remove the process from the dictionary
        del process_dict[job_id]


def input_cam_url(config):
    CAM_HOST = config["CAM_HOST"]
    CAM_USER = config["CAM_USER"]
    CAM_PASS = config["CAM_PASS"]
    INPUT_CAM = f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_HOST}:554/Streaming/channels/101/"
    return INPUT_CAM


def stream_game(duration=(60 * 4), key="", config={}, name=""):
    logging.info("Starting a stream...")
    duration = int(duration)

    INPUT_CAM = input_cam_url(config)

    # Game Changer Settings
    GC_BASE = "rtmps://601c62c19c9e.global-contribute.live-video.net:443/app"

    if key:
        GC_KEY = key
    else:
        logging.error("No Destionation GC Key Given")
        return

    OUTPUT_GC1 = f"{GC_BASE}/{GC_KEY}"

    # ffmpeg options
    LOG_OPTS = "-hide_banner -loglevel error -stats -report "
    RSTP_OPTS = "-rtsp_transport tcp "
    VIDEO_OPTS = "-c:v copy -bufsize 12000k -g 60 "
    AUDIO_OPTS = "-c:a aac -b:a 128k"

    # Single output
    OUTPUT = f'-f flv "{OUTPUT_GC1}" '

    FFMPEG_BIN="/usr/bin/ffmpeg" # OS Package
    # FFMPEG_BIN="/usr/local/bin/ffmpeg "  # local compile, not working reliably

    pretty_name = name.replace(" ", "_")
    cmd = f'FFREPORT="level=32:file=logs/%p-%t-{pretty_name}.log" {FFMPEG_BIN} '  # apt install

    cmd += f"{LOG_OPTS} -thread_queue_size 256 "
    cmd += f"{RSTP_OPTS} -i {INPUT_CAM} "
    cmd += f"{VIDEO_OPTS} {AUDIO_OPTS} -t {duration} "
    cmd += f"{OUTPUT}"

    run_bash_command(cmd)


def snapshot(config={}):
    INPUT_CAM = input_cam_url(config)

    # Use the second channel for the snapshot
    INPUT_CAM = INPUT_CAM.replace("channels/101", "channels/102")
    cmd = f"/usr/bin/ffmpeg -hide_banner -loglevel error -y -i {INPUT_CAM} -frames:v 1 -q:v 2 streamSchedule/static/images/field.jpg"
    run_bash_command(cmd)


# jinja2 doesn't have easy date formatting
def format_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    """Format a datetime object to a string using strftime."""
    if value is None:
        return ""
    return value.strftime(format)

# Map jinja function for formatting dates/times
app.jinja_env.filters["datetime"] = format_datetime

# initialize scheduler
jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.db")}
scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()


@auth.verify_password
def verify_password(username, password):
    authDict = SECRETS.get("AUTH", {})

    logger.info(f"Checking password for {username}")
    if username in authDict and  bcrypt.check_password_hash(authDict[username], password):
        return username


# todo require auth
@app.route("/")
def nohit():
    return redirect("https://sfll.org/", code=302)
    # abort(404)

# List current jobs
@app.route("/list")
@auth.login_required
def list():
    jobs = sorted(scheduler.get_jobs(), key=lambda x: x.next_run_time)
    return render_template("list.html.j2", jobs=jobs)

@app.route("/add")
@auth.login_required
def add():
    return render_template("add.html.j2")

@app.route("/submit", methods=["POST"])
@auth.login_required
def submit():
    # Get the name from the form
    logger.info(request.form)
    teamName = request.form.get("teamName")
    streamDate = request.form.get("date")
    streamStartTime = request.form.get("startTime")
    streamEndTime = request.form.get("endTime")
    streamKey = request.form.get("streamKey")

    # Parse the date and time
    try:
        date_obj = datetime.strptime(streamDate, "%Y-%m-%d").date()
    except ValueError:
        abort(500, "Unable to understand your date, please do back and try again")

    try:
        start_time_obj = datetime.strptime(streamStartTime, "%H:%M").time()
        end_time_obj = datetime.strptime(streamEndTime, "%H:%M").time()
    except ValueError:
        abort(500, "Unable to understand your time fields. Please go back and try again.")

    # Store data to log
    #data = f"{teamName},{start_datetime_obj},{end_datetime_obj},{streamKey}"
    #with open('submissions.log', 'a') as file:
    #    file.write(data + '\n')

    # Combine into a datetime object
    start_datetime_obj = datetime.combine(date_obj, start_time_obj)
    end_datetime_obj = datetime.combine(date_obj, end_time_obj)

    calculated_duration = end_datetime_obj - start_datetime_obj
    calculated_duration_seconds = int(calculated_duration.total_seconds())

    # logger.info(f"NAME:  {teamName}")
    # logger.info(f"START: {start_datetime_obj}")
    # logger.info(f"END:   {end_datetime_obj}")
    # logger.info(
    #     f"DUR:   {calculated_duration_seconds}s {calculated_duration_seconds / 60}min"
    # )

    new_stream(
        teamName,
        startTime=start_datetime_obj,
        duration=calculated_duration_seconds,
        key=streamKey,
        config=SECRETS,
    )
    return redirect(url_for("list"))

# # unprotected inputs
# @app.route(f"/{SECRETS.get('LONG_STRING')}/list")
# def list2():
#     return list()

# @app.route(f"/{SECRETS.get('LONG_STRING')}/add")
# def add2():
#     return add()

# @app.route(f"/{SECRETS.get('LONG_STRING')}/submit",  methods=["POST"])
# def submit2():
#     return submit()
# FIXME: Can we make the url_for a parameter?


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
            stream_game,
            trigger="date",
            run_date=startTime,
            id=name,
            name=name,
            kwargs={"duration": duration, "key": key, "config": config, "name": name},
        )
    except ConflictingIdError:
        logger.info(f"Job '{name}' Already Seen")
        pass


# Background Job - Image Snapshots every 5m
now = datetime.now()
start_at_top_of_next_minute = now + timedelta(
    seconds=(60 - now.second), microseconds=(-now.microsecond)
)

try:
    scheduler.add_job(
        id="HIDDEN-Snapshots",
        name="Field Snapshot",
        func=snapshot,
        kwargs={
            "config": SECRETS,
        },
        trigger=IntervalTrigger(start_date=start_at_top_of_next_minute, minutes=5),
    )
except ConflictingIdError:
    logger.info("Job Already Exists")
    pass


if __name__ == "__main__":
    app.run(debug=True)
