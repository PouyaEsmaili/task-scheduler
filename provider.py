from datetime import datetime
from queue import PriorityQueue
from typing import Optional


class Provider:
    name: str
    rate: float
    last_request_time: Optional[datetime]
    is_active: bool

    def __init__(self, name: str, rate: float):
        self.name = name
        self.rate = rate
        self.last_request_time = None
        self.is_active = True

    @property
    def _duration(self) -> float:
        return 1 / self.rate

    def _is_ready(self) -> bool:
        if self.last_request_time is None:
            return True
        return (datetime.now() - self.last_request_time).total_seconds() >= self._duration

    def is_available(self) -> bool:
        return self._is_ready() and self.is_active

    def available_in(self) -> float:
        if self.last_request_time is None:
            return 0
        min_wait_time = 0
        if not self.is_active:
            min_wait_time = 0.001
        return max(min_wait_time, self._duration - (datetime.now() - self.last_request_time).total_seconds())


class ProviderMeta(Provider):
    task_queue: PriorityQueue
    probability: float

    def __init__(self, probability, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_queue = PriorityQueue()
        self.probability = probability

    def min_execute_after(self):
        return min(map(lambda x: x.execute_after, self.task_queue.queue))


class ThirdPartyProvider(Provider):
    async def view(self, payload):
        if not self.is_active:
            raise Exception(f'Provider {self.name} is not active')
        if not self.is_available():
            raise Exception(f'Provider {self.name} rate limit exceeded')
        print(f'Received {payload} in {self.name}')
        self.last_request_time = datetime.now()
