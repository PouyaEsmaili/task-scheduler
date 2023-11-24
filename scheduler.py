import asyncio
from datetime import datetime
from typing import List, Dict

from provider import ProviderMeta, ThirdPartyProvider
from task import Task


class Scheduler:
    providers: Dict[str, ProviderMeta]
    third_party_providers: Dict[str, ThirdPartyProvider]

    def __init__(self, provider_options: List[Dict]):
        for i, option in enumerate(provider_options):
            name = option['name']
            rate = option['rate']
            provider = ProviderMeta(name, rate)
            self.providers[name] = provider
            third_party_provider = ThirdPartyProvider(name, rate)
            self.third_party_providers[name] = third_party_provider

    def schedule(self, provider_name: str, payload: str, priority: int):
        task = Task(provider_name, payload, priority)
        provider = self.providers[provider_name]
        provider.task_queue.put((priority, task))
        if provider.is_available():
            asyncio.run(self._run_task(provider))
        else:
            asyncio.run(self._scheduled_run_task(provider))

    async def _run_task(self, provider: ProviderMeta):
        task = provider.task_queue.get()
        third_party_provider = self.third_party_providers[provider.name]
        provider.last_request_time = datetime.now()
        try:
            await third_party_provider.view(task.payload)
        except Exception as e:
            print(e)

    async def _scheduled_run_task(self, provider: ProviderMeta):
        while not provider.is_available():
            available_in = provider.available_in()
            await asyncio.sleep(available_in)
        await self._run_task(provider)
