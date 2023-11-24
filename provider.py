from datetime import datetime
from queue import PriorityQueue
from typing import Optional


class Provider:
    name: str
    rate: float
    last_request_time: Optional[datetime]

    def __init__(self, name: str, rate: float):
        self.name = name
        self.rate = rate
        self.last_request_time = None

    @property
    def _duration(self) -> float:
        return 1 / self.rate

    def _is_ready(self) -> bool:
        if self.last_request_time is None:
            return True
        return (datetime.now() - self.last_request_time).total_seconds() >= self._duration

    def is_available(self) -> bool:
        return self._is_ready()

    def available_in(self) -> float:
        if self.last_request_time is None:
            return 0
        return max(0.0, self._duration - (datetime.now() - self.last_request_time).total_seconds())


class ProviderMeta(Provider):
    task_queue: PriorityQueue

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_queue = PriorityQueue()


class ThirdPartyProvider(Provider):
    def view(self, payload):
        if not self.is_available():
            raise Exception(f'Provider {self.name} rate limit exceeded')
        print(f'Received {payload} in {self.name}')
        self.last_request_time = datetime.now()
