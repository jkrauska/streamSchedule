import logging
import subprocess
import time
from datetime import datetime
from apscheduler.events import JobExecutionEvent
from flask import current_app


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# sample task
def task_function():
    print("Example Task is running...")
    time.sleep(1)
    print("Example Task Done")


# Define a function to run a subprocess in Bash
def run_bash_command(cmd):
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


def stream_game(duration=(60*4), key="", config={}):

    duration=int(duration)

    CAM_HOST = config['CAM_HOST']
    CAM_USER=config['CAM_USER']
    CAM_PASS=config['CAM_PASS']
    INPUT_CAM=f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_HOST}:554/Streaming/channels/101/"

    # Game Changer Settings
    GC_BASE="rtmps://601c62c19c9e.global-contribute.live-video.net:443/app"

    if key:
        GC_KEY = key
    else:    
        logging.error("No Destionation GC Key Given")
        return


    OUTPUT_GC1=f"{GC_BASE}/{GC_KEY}"

    logger.info(f"INPUT:    {INPUT_CAM}")
    logger.info(f"OUTPUT1:  {OUTPUT_GC1}")
    logger.info(f"DURATION: {duration} seconds")

    # ffmpeg options
    LOG_OPTS="-hide_banner -loglevel error -stats -report "
    RSTP_OPTS="-rtsp_transport tcp "
    VIDEO_OPTS="-c:v copy -bufsize 12000k -g 60 "
    AUDIO_OPTS="-c:a aac -b:a 128k"

    # Single output
    OUTPUT=f"-f flv \"{OUTPUT_GC1}\" "

    # # Dual Output  ( COULD NOT GET WORKING, use two independent jobs)
    #OUTPUT=f"""-f tee -map 0  "[f=flv:onfail=ignore]{OUTPUT_GC1}|[f=flv:onfail=ignore]{OUTPUT_GC2}" """

    # cmd = "/usr/local/bin/ffmpeg "  # local compile, not working reliably

    cmd = "/usr/bin/ffmpeg "  # apt install

    cmd += f"{LOG_OPTS} -thread_queue_size 256 "
    cmd += f"{RSTP_OPTS} -i {INPUT_CAM} "
    cmd += f"{VIDEO_OPTS} {AUDIO_OPTS} -t {duration} "
    cmd += f"{OUTPUT}"

    logger.info(f"Running {cmd}")
    run_bash_command(cmd)
    logger.info("Completed")
