import asyncio
import queue
from datetime import datetime
from typing import List, Dict

from provider import ProviderMeta, ThirdPartyProvider
from task import Task


class Scheduler:
    providers: Dict[str, ProviderMeta]
    third_party_providers: Dict[str, ThirdPartyProvider]

    def __init__(self, provider_options: List[Dict]):
        self.providers = {}
        self.third_party_providers = {}

        probability_weight_sum = sum(map(lambda x: x['weight'], provider_options))
        for i, option in enumerate(provider_options):
            name = option['name']
            rate = option['rate']
            probability = option['weight'] / probability_weight_sum
            provider = ProviderMeta(probability, name, rate)
            self.providers[name] = provider
            third_party_provider = ThirdPartyProvider(name, rate)
            self.third_party_providers[name] = third_party_provider

    @property
    def is_empty(self):
        return all(map(lambda x: x.task_queue.empty(), self.providers.values()))

    def schedule(self, provider_name: str, payload: str, priority: int, execute_after: datetime = None):
        task = Task(provider_name, payload, priority, execute_after)
        provider = self.providers[provider_name]
        provider.task_queue.put(task)
        if provider.is_available() and execute_after < datetime.now():
            asyncio.create_task(self._run_task(provider))
        else:
            asyncio.create_task(self._scheduled_run_task(provider))

    async def _run_task(self, provider: ProviderMeta):
        task = provider.task_queue.get()
        not_ready_tasks = []
        while task.execute_after > datetime.now():
            not_ready_tasks.append(task)
            try:
                task = provider.task_queue.get(block=False)
            except queue.Empty as e:
                for t in not_ready_tasks:
                    provider.task_queue.put(t)
                return
        for t in not_ready_tasks:
            provider.task_queue.put(t)

        third_party_provider = self.third_party_providers[provider.name]
        try:
            await third_party_provider.view(task.payload)
        except Exception as e:
            print(e)
        finally:
            provider.last_request_time = datetime.now()

    async def _scheduled_run_task(self, provider: ProviderMeta):
        min_execute_after_seconds = (provider.min_execute_after() - datetime.now()).total_seconds()
        while not provider.is_available() or min_execute_after_seconds > 0:
            available_in = provider.available_in()
            await asyncio.sleep(max(min_execute_after_seconds, available_in))
        await self._run_task(provider)
