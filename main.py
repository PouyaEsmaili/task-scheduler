import argparse
import asyncio
import sys
import threading

import yaml

from generator import TaskGenerator
from scheduler import Scheduler


def parse_yaml_config(file_name):
    try:
        with open(file_name, 'r') as file:
            config_data = yaml.safe_load(file)
            return config_data
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file '{file_name}': {e}")
        return None


async def ainput() -> str:
    return (await asyncio.to_thread(sys.stdin.readline)).rstrip('\n')


async def read_input(stop_event: asyncio.Event, scheduler: Scheduler):
    while True:
        try:
            line = await ainput()
            if line == 'exit':
                stop_event.set()
                print('Stopping...')
                break
            elif line in scheduler.providers:
                provider = scheduler.providers[line]
                provider.is_active = not provider.is_active
                print(f'Provider {provider.name} is {"active" if provider.is_active else "inactive"}')
            else:
                print('Unknown command.')
        except asyncio.CancelledError:
            break


async def main():
    parser = argparse.ArgumentParser(description='Parse YAML configuration file.')
    parser.add_argument('-c', '--config', type=str, help='Path to the YAML configuration file')

    args = parser.parse_args()
    config = args.config

    config_data = parse_yaml_config(config)

    if config_data:
        print("Parsed YAML configuration:")
        print(config_data)

    scheduler = Scheduler(config_data['providers'])
    generator = TaskGenerator(scheduler, config_data['inter_arrival_time_rate'])

    stop_event = asyncio.Event()

    asyncio.create_task(read_input(stop_event, scheduler))

    await generator.run(stop_event)


if __name__ == '__main__':
    asyncio.run(main())

