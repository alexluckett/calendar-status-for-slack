from exceptions import UserException
from slackclient import SlackClient


class SlackStatusUpdater:

    def __init__(self, token):
        try:
            self.slack_api = SlackClient(token)
        except:
            raise UserException("No API key provided", "")

    def get_status_emoji(self, status_message):
        return {
            "in a meeting": ":calendar:",
            "available": ":tea:",
            "on holiday": ":palm_tree:",
            "commuting": ":bus:",
            "": ""  # reset status
        }.get(status_message.lower(), "")

    def update_status(self, emoji_name, message=None):
        try:
            profile_payload = {}

            if emoji_name:
                profile_payload["status_emoji"] = emoji_name
            else:
                profile_payload["status_emoji"] = ""

            if message:
                profile_payload["status_text"] = message
            else:
                profile_payload["status_text"] = ""

            if profile_payload:
                print("Contacting Slack Web API")
                response = self._call_slack_api("users.profile.set", profile=profile_payload)
                print("\n\nResponse from API:")
                print(response)
        except Exception as e:
            raise UserException("Unable to update slack status.", str(e))

    def _call_slack_api(self, method, **kwargs):
        from requests.exceptions import ConnectionError

        try:
            return self.slack_api.api_call(method, **kwargs, timeout=1)
        except ConnectionError as e:
            import logging

            logging.exception("Failed to connect to slack")
            pass  # user might be offline. ignore for now.
            #raise UserException("Connection to Slack failed", str(e))


