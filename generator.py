import asyncio
import random
from datetime import datetime, timedelta

from scheduler import Scheduler


class TaskGenerator:
    scheduler: Scheduler
    expo_lambda: float

    def __init__(self, scheduler: Scheduler, expo_lambda: float):
        self.scheduler = scheduler
        self.expo_lambda = expo_lambda

    async def run(self, stop_event: asyncio.Event):
        index = 0
        while not stop_event.is_set():
            inter_arrival_time = random.expovariate(self.expo_lambda)
            await asyncio.sleep(inter_arrival_time)
            provider_name = random.choices(
                list(self.scheduler.providers.keys()),
                weights=list(map(lambda x: x.probability, self.scheduler.providers.values()))
            )[0]
            priority = random.randint(1, 10)
            execute_after_seconds = random.expovariate(5)
            execute_after = datetime.now() + timedelta(seconds=execute_after_seconds)
            self.scheduler.schedule(provider_name, f'payload_{index}', priority, execute_after)
            index += 1

        while not self.scheduler.is_empty:
            await asyncio.sleep(1)
