from abc import ABC, abstractmethod
import datetime
import pandas as pd

import warnings
warnings.filterwarnings("ignore", 'This pattern has match groups')


class RecentEventsProvider(ABC):

    def get_recent_events(self):
        now = datetime.datetime.now()
        begin = now - datetime.timedelta(days=14)
        end = now + datetime.timedelta(days=14)

        event_list = self.get_events(begin, end)

        schema = ['Title', 'Organizer', 'Start', 'End', 'Duration(Minutes)', 'Busy_Status', 'Response_Status']

        return self.convert_events_list_to_dataframe(schema, event_list)

    @abstractmethod
    def get_events(self, start_datetime, end_datetime):
        pass

    @abstractmethod
    def convert_events_list_to_dataframe(self, schema, event_list):
        pass

    def get_event_breakdown(self, organiser_name):
        return EventBreakdown(self.get_recent_events(), organiser_name)


class EventBreakdown:

    def __init__(self, event_df, organiser_name):
        self.event_df = event_df
        self.organiser_name = organiser_name

        self.keep_busy_statuses = ["Organiser", "Tentatively accepted", "Accepted"]

    def get_current_accepted_events(self):
        now = datetime.datetime.now()  # THIS IS USED BELOW, just not directly in this file
        current = self.event_df.query("Start <= @now & End > @now")

        current_accepted = current[current["Response_Status"].isin(self.keep_busy_statuses)]
        current_organiser = current[current["Organizer"] == self.organiser_name]

        current_accepted = pd.concat([current_organiser, current_accepted])

        return current_accepted

    def is_currently_busy(self):
        current_accepted = self.get_current_accepted_events()

        current_but_busy = current_accepted.query("Busy_Status != 'Available'")

        return current_but_busy.shape[0] > 0

    def is_on_annual_leave(self):
        mask = self.event_df["Organizer"] == self.organiser_name

        df = self.event_df[mask]
        annual_leave = df[df["Title"].str.contains(r"\b(annual leave|AL|holiday)\b", case=False)]

        return annual_leave.shape[0] > 0


def get_updated_status_message(event_provider: RecentEventsProvider):
    event_breakdown: EventBreakdown = event_provider.get_event_breakdown("Luckett, Alex")

    if event_breakdown.is_on_annual_leave():
        return "On holiday"
    elif event_breakdown.is_currently_busy():
        return "In a meeting"
    else:
        return ""
