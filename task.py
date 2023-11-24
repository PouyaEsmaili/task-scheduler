from datetime import datetime


class Task:
    provider_name: str
    payload: str
    priority: int
    execute_after: datetime

    def __init__(self, provider_name: str, payload: str, priority: int, execute_after: datetime):
        self.provider_name = provider_name
        self.payload = payload
        self.priority = priority
        self.execute_after = execute_after

    def __lt__(self, other):
        return self.priority < other.priority

    def __le__(self, other):
        return self.priority <= other.priority

    def __gt__(self, other):
        return self.priority > other.priority

    def __ge__(self, other):
        return self.priority >= other.priority

    def __eq__(self, other):
        return self.priority == other.priority

    def __ne__(self, other):
        return self.priority != other.priority
