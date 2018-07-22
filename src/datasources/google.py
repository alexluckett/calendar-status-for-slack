import datetime

from datasources import RecentEventsProvider
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file as _file, client, tools
import pandas as pd
import os


class GoogleCalendar(RecentEventsProvider):

    def convert_events_list_to_dataframe(self, schema, event_list):
        return pd.DataFrame(columns=schema, data=event_list)

    def __init__(self, general_config, config):
        super(GoogleCalendar, self).__init__(general_config, config)

        # Setup the Calendar API
        SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

        store_file_path = os.path.join(self.general_config.get("rundir", ""), "token.json")
        credential_file_path = self.config["credfile"]

        store = _file.Storage(store_file_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flags = tools.argparser.parse_args([])

            flow = client.flow_from_clientsecrets(credential_file_path, SCOPES)
            credentials = tools.run_flow(flow, store, flags)

        service = build('calendar', 'v3', http=credentials.authorize(Http()))

        self.google_service = service

    def get_events(self, start_datetime, end_datetime):
        # Call the Calendar API

        start_formatted = start_datetime.isoformat() + "Z"
        end_formatted = end_datetime.isoformat() + "Z"

        events_result = self.google_service.events().list(calendarId='primary', singleEvents=True, orderBy='startTime',
                                                          timeMin=start_formatted, timeMax=end_formatted).execute()
        events = events_result.get('items', [])

        events_converted = [convert_to_schema(event) for event in events]

        return events_converted


def convert_to_schema(google_event):
    try:
        start = google_event["start"]["dateTime"]
    except KeyError:
        start = google_event["start"]["date"]

    try:
        end = google_event["end"]["dateTime"]
    except KeyError:
        end = google_event["end"]["date"]

    return [
        google_event.get("summary", ""),
        google_event["creator"]["displayName"],
        start,
        end,
        transparency_to_busy_status(google_event),
        _status_to_standard_format(google_event["status"])
    ]


def _status_to_standard_format(status_message):
    return {
        "confirmed": "Accepted",
        "tentative": "Tentatively accepted",
        "cancelled": "Not required"
    }[status_message]

def transparency_to_busy_status(google_event):
    transparency = google_event.get("transparency", "transparent")

    return {
        "opaque": "Busy",
        "transparent": "Available"
    }[transparency]