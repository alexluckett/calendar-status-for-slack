import os
import logging
from datasources import get_updated_status_message
from datasources import get_event_provider
from slack.SlackStatusUpdater import SlackStatusUpdater
from exceptions import UserException
from win32api import MessageBox
from config import ConfigStorage, get_command_line_args


########################################################
# Initial setup - get settings from args/config file
########################################################

command_line_args = get_command_line_args()
config_file = command_line_args.config

config_storage = ConfigStorage(config_file)

run_directory = config_storage.get_general_config()["rundir"]
force_run = config_storage.get_general_config()["force"]
default_provider = config_storage.get_general_config()["provider"]

slack_token = config_storage.get_application_config("slack")["token"]

status_message_path = os.path.join(run_directory, "previous_status.txt")
log_file_path = os.path.join(run_directory, "automate.log")


########################################################
# Set up logging
########################################################

logging.basicConfig(filename=log_file_path, level=logging.DEBUG,
                    format="*** %(asctime)s: %(levelname)-8s - %(module)25s - %(funcName)-30s[%(lineno)3s]: %(message)s")
logging.getLogger().addHandler(logging.StreamHandler())


########################################################
# Functions and main code calls
########################################################

def get_old_status():
    try:
        with open(status_message_path, "r") as f:
            data = f.read()
    except FileNotFoundError:
        return ""

    return data


def update(slack_wrapper, status_message, emoji, force_write=False):
    old_status = get_old_status()

    logging.info("Old status: {}".format(old_status))
    logging.info("New status: {}".format(status_message))

    if force_write or old_status != status_message:
        with open(status_message_path, mode='w') as _file:
            _file.write(status_message)
            logging.info("Writing to file")

        slack_wrapper.update_status(emoji, message=status_message)


def main():
    try:
        event_provider = get_event_provider(default_provider, config_storage)
        slack_wrapper = SlackStatusUpdater(slack_token)

        status_message = get_updated_status_message(event_provider, config_storage)
        emoji = slack_wrapper.get_status_emoji(status_message)

        logging.info("Detected status: {}".format(status_message))
        logging.info("Detected emoji: {}".format(emoji))

        update(slack_wrapper, status_message, emoji, force_write=force_run)
    except UserException as e:
        MessageBox(0, "{}. \r\n\r\n{}".format(e.message, e.details), "Slack Status Updater Error")
        logging.exception("User exception encountered")
    except Exception:
        logging.exception("A fatal error occurred")


if __name__ == "__main__":
    main()