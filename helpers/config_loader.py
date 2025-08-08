import yaml

class ConfigLoader:
    def __init__(self, agents_path="config/agents.yaml", tasks_path="config/tasks.yaml"):
        self.agents_path = agents_path
        self.tasks_path = tasks_path

    def load_agents(self):
        return self._load_yaml(self.agents_path)

    def load_tasks(self):
        return self._load_yaml(self.tasks_path)

    def _load_yaml(self, path):
        with open(path, 'r') as file:
            return yaml.safe_load(file)
