import win32com.client
import pandas as pd

from datasources import RecentEventsProvider


OUTLOOK_DATE_FORMAT = '%m/%d/%Y %H:%M'


class OutlookLocalAPI(RecentEventsProvider):

    def __init__(self, general_config, config):
        super(OutlookLocalAPI, self).__init__(general_config, config)

        outlook = win32com.client.Dispatch("Outlook.Application")
        ns = outlook.GetNamespace("MAPI")

        self.appointments = ns.GetDefaultFolder(9).Items

    def get_events(self, start_datetime, end_datetime):
        """
        Returns events within the last 2 days (+/- 1 day from now)
        :return: list of appointmentItems
        """

        outlook_date_format = "%d/%m/%Y %I:%M %p"
        restriction = "[Start] > '" + start_datetime.strftime(outlook_date_format) + "' And [End] < '" + \
                      end_datetime.strftime(outlook_date_format) + "'"

        self.appointments.IncludeRecurrences = "True"
        self.appointments.Sort("[Start]", False)
        restricted_items = self.appointments.Restrict(restriction)

        return restricted_items

    def convert_events_list_to_dataframe(self, schema, event_list):
        event_list = []

        for appointment_item in event_list:
            event_list.append([
                appointment_item.Subject,
                appointment_item.Organizer,
                appointment_item.Start.Format(OUTLOOK_DATE_FORMAT),
                appointment_item.End.Format(OUTLOOK_DATE_FORMAT),
                appointment_item.BusyStatus,
                appointment_item.ResponseStatus,
            ])

        df = pd.DataFrame(columns=schema, data=event_list)
        apply_to_df_inplace(df, "Busy_Status", _convert_busy_status_to_string)
        apply_to_df_inplace(df, "Response_Status", _convert_response_status_to_string)

        return df


def _convert_busy_status_to_string(status_number):
    return [
        "Available",
        "Tentative",
        "Busy",
        "Out of office",
        "Working elsewhere"
    ][status_number]


def _convert_response_status_to_string(status_number):
    return [
        "Not required",
        "Organiser",
        "Tentatively accepted",
        "Accepted",
        "Declined",
        "Not responded"
    ][status_number]


def apply_to_df_inplace(df, column, func):
    df.loc[:, column] = df[column].apply(func)