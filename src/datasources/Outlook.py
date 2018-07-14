import datetime
import logging

import win32com.client
import pandas as pd

from datasources import RecentEventsProvider


OUTLOOK_DATE_FORMAT = '%m/%d/%Y %H:%M'
keep_busy_statuses = ["Organiser", "Tentatively accepted", "Accepted"]


class OutlookLocalAPI(RecentEventsProvider):

    def __init__(self):
        outlook = win32com.client.Dispatch("Outlook.Application")
        ns = outlook.GetNamespace("MAPI")

        self.appointments = ns.GetDefaultFolder(9).Items

    def get_recent_events(self):
        """
        Returns events within the last 2 days (+/- 1 day from now)
        :return: list of appointmentItems
        """

        now = datetime.datetime.now()
        begin = now - datetime.timedelta(days=14)
        end = now + datetime.timedelta(days=14)

        outlook_date_format = "%d/%m/%Y %I:%M %p"
        restriction = "[Start] > '" + begin.strftime(outlook_date_format) + "' And [End] < '" + end.strftime(
            outlook_date_format) + "'"

        self.appointments.IncludeRecurrences = "True"
        self.appointments.Sort("[Start]", False)
        restricted_items = self.appointments.Restrict(restriction)

        return restricted_items


def _appointment_item_to_list(appointment_item):
    return [
        appointment_item.Subject,
        appointment_item.Organizer,
        appointment_item.Start.Format(OUTLOOK_DATE_FORMAT),
        appointment_item.End.Format(OUTLOOK_DATE_FORMAT),
        appointment_item.Duration,
        appointment_item.BusyStatus,
        appointment_item.ResponseStatus
    ]


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


def convert_appointments_to_dataframe(appointment_item_list):
    schema = ['Title', 'Organizer', 'Start', 'End', 'Duration(Minutes)', 'Busy_Status', 'Response_Status']

    data = []
    for appointmentItem in appointment_item_list:
        data.append(_appointment_item_to_list(appointmentItem))

    df = pd.DataFrame(columns=schema, data=data)
    apply_to_df_inplace(df, "Busy_Status", _convert_busy_status_to_string)
    apply_to_df_inplace(df, "Response_Status", _convert_response_status_to_string)

    df["Start"] = pd.to_datetime(df["Start"])
    df["End"] = pd.to_datetime(df["End"])

    return df, schema


def _is_on_annual_leave(df, organiser):
    df = df[df["Organizer"] == organiser]
    annual_leave = df[df["Title"].str.contains(r"\b(annual leave|AL|holiday)\b", case=False)]

    return annual_leave.shape[0] > 0


def get_updated_status_message(outlook_api):
    appointments = outlook_api.get_recent_events()
    df, schema = convert_appointments_to_dataframe(appointments)

    now = datetime.datetime.now()
    current = df.query("Start <= @now & End > @now")

    current_accepted = current[current["Response_Status"].isin(keep_busy_statuses)]
    current_organiser = current[current["Organizer"] == "Luckett, Alex"]

    current_accepted = pd.concat([current_organiser, current_accepted])

    current_but_busy = current_accepted.query("Busy_Status != 'Available'")

    annual_leave = _is_on_annual_leave(current_accepted, "Luckett, Alex")

    if annual_leave:
        return "On holiday"
    elif current_but_busy.shape[0] > 0:
        return "In a meeting"
    elif (now.hour < 9 or 17 <= now.hour < 19) and now.weekday() != 4:  # not before or after work, or a Friday WFH
        return "Commuting"
    else:
        return ""
