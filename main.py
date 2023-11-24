import argparse
import yaml

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


def main():
    parser = argparse.ArgumentParser(description='Parse YAML configuration file.')
    parser.add_argument('-c', '--config', type=str, help='Path to the YAML configuration file')

    args = parser.parse_args()
    config = args.config

    config_data = parse_yaml_config(config)

    if config_data:
        print("Parsed YAML configuration:")
        print(config_data)

    scheduler = Scheduler(config_data['providers'])



if __name__ == '__main__':
    main()

