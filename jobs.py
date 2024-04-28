import logging
import subprocess
import time


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

process_dict = {}


# sample task
def task_function():
    print("Example Task is running...")
    time.sleep(1)
    print("Example Task Done")


# Define a function to run a subprocess in Bash
def run_bash_command(cmd):

    # Start a subprocess (for example, a simple shell command)
    proc = subprocess.run(cmd, shell=True)
    # Store the process handle with a unique job identifier
    process_dict[cmd] = proc
    # print(f"Started job {cmd} -- \n\n  {proc}\n\n")
    # print(process_dict)

    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


def stop_subprocess(job_id):
    # Retrieve the process handle
    proc = process_dict.get(job_id)
    if proc:
        # Terminate the process
        proc.terminate()
        print(f"Stopped job {job_id}")
        # Remove the process from the dictionary
        del process_dict[job_id]


def cam_url(config):
    CAM_HOST = config["CAM_HOST"]
    CAM_USER = config["CAM_USER"]
    CAM_PASS = config["CAM_PASS"]
    INPUT_CAM = f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_HOST}:554/Streaming/channels/101/"
    return INPUT_CAM


def stream_game(duration=(60 * 4), key="", config={}, name=""):
    duration = int(duration)
    INPUT_CAM = cam_url(config)

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

    # # Dual Output  ( COULD NOT GET WORKING, use two independent jobs)
    # OUTPUT=f"""-f tee -map 0  "[f=flv:onfail=ignore]{OUTPUT_GC1}|[f=flv:onfail=ignore]{OUTPUT_GC2}" """

    # cmd = "/usr/local/bin/ffmpeg "  # local compile, not working reliably

    pretty_name = name.replace(" ", "_")
    cmd = f'FFREPORT="level=32:file=logs/%p-%t-{pretty_name}.log" /usr/bin/ffmpeg '  # apt install

    cmd += f"{LOG_OPTS} -thread_queue_size 256 "
    cmd += f"{RSTP_OPTS} -i {INPUT_CAM} "
    cmd += f"{VIDEO_OPTS} {AUDIO_OPTS} -t {duration} "
    cmd += f"{OUTPUT}"
    run_bash_command(cmd)


def snapshot(config={}):
    INPUT_CAM = cam_url(config)

    # Use the second channel for the snapshot
    INPUT_CAM = INPUT_CAM.replace("channels/101", "channels/102")
    cmd = f"/usr/bin/ffmpeg -hide_banner -loglevel error -y -i {INPUT_CAM} -frames:v 1 -q:v 2 streamSchedule/static/images/field.jpg"
    run_bash_command(cmd)
