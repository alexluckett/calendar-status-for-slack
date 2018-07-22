from datasources.base_providers import EventBreakdown, RecentEventsProvider
from datasources.outlook import OutlookLocalAPI
from datasources.google import GoogleCalendar
from config import ConfigStorage


_event_providers = {
    "outlook_local": OutlookLocalAPI,
    "google_calendar": GoogleCalendar
}


def get_event_provider(provider_name, config_storage):
    try:
        general_config = config_storage.get_general_config()
    except KeyError:
        general_config = {}

    try:
        provider_config = config_storage.get_application_config(provider_name)
    except ValueError:
        provider_config = {}

    try:
        provider = _event_providers[provider_name.lower()]
    except KeyError:
        raise ValueError("Invalid event provider name provided")

    return provider(general_config, provider_config)


def get_updated_status_message(event_provider: RecentEventsProvider, config_storage: ConfigStorage):
    calendar_name = config_storage.get_general_config()["fullname"]
    event_breakdown: EventBreakdown = event_provider.get_event_breakdown(calendar_name)

    if event_breakdown.is_on_annual_leave():
        return "On holiday"
    elif event_breakdown.is_currently_busy():
        return "In a meeting"
    else:
        return ""
