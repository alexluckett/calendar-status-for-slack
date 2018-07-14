from abc import ABC, abstractmethod


class RecentEventsProvider(ABC):

    @abstractmethod
    def get_recent_events(self):
        pass
