import logging
from datasources.outlook import OutlookLocalAPI
from datasources import get_updated_status_message
from datasources import get_event_provider
from slack.SlackStatusUpdater import SlackStatusUpdater
from exceptions import UserException
from win32api import MessageBox
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument("--token", type=str, required=True)
parser.add_argument("--rundir", type=str, required=True)
parser.add_argument("--force", type=bool, default=False)

args = parser.parse_args()

run_directory = args.rundir
token = args.token
force = args.force

status_message_path = "{}\\previous_status.txt".format(run_directory)

logging.basicConfig(filename="{}\\automate.log".format(run_directory), level=logging.DEBUG,
                    format="*** %(asctime)s: %(levelname)-8s - %(module)25s - %(funcName)-30s[%(lineno)3s]: %(message)s")
logging.getLogger().addHandler(logging.StreamHandler())


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
        event_provider = get_event_provider("outlook_local")
        slack_wrapper = SlackStatusUpdater(token)

        status_message = get_updated_status_message(event_provider)
        emoji = slack_wrapper.get_status_emoji(status_message)

        logging.info("Detected status: {}".format(status_message))
        logging.info("Detected emoji: {}".format(emoji))

        update(slack_wrapper, status_message, emoji, force_write=force)
    except UserException as e:
        MessageBox(0, "{}. \r\n\r\n{}".format(e.message, e.details), "Slack Status Updater Error")
        logging.exception("User exception encountered")
    except Exception:
        logging.exception("A fatal error occurred")


if __name__ == "__main__":
    main()