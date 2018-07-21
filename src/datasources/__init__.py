from datasources.base_providers import EventBreakdown, RecentEventsProvider
from datasources.outlook import OutlookLocalAPI


def get_event_provider(provider_name):
    try:
        return {
            "outlook_local": OutlookLocalAPI()
        }[provider_name]
    except KeyError:
        raise ValueError("Invalid event provider name provided")


def get_updated_status_message(event_provider: RecentEventsProvider):
    event_breakdown: EventBreakdown = event_provider.get_event_breakdown("Luckett, Alex")

    if event_breakdown.is_on_annual_leave():
        return "On holiday"
    elif event_breakdown.is_currently_busy():
        return "In a meeting"
    else:
        return ""
