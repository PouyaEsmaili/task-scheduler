class Task:
    provider_name: str
    payload: str
    priority: int

    def __init__(self, provider_name: str, payload: str, priority: int):
        self.provider_name = provider_name
        self.payload = payload
        self.priority = priority
