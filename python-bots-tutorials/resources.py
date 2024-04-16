import json

class Resources:
    def __init__(self, user_id, resource_name, file_path='resource_data.json'):
        self.user_id = str(user_id)
        self.resource_name = resource_name
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def _save_data(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def value(self):
        return self.data.get(self.user_id, {}).get(self.resource_name, 0)

    def add(self, amount):
        user_data = self.data.setdefault(self.user_id, {})
        current_value = user_data.setdefault(self.resource_name, 0)
        user_data[self.resource_name] = current_value + amount
        self._save_data()

    def cut(self, amount):
        user_data = self.data.setdefault(self.user_id, {})
        current_value = user_data.setdefault(self.resource_name, 0)
        user_data[self.resource_name] = max(0, current_value - amount)
        self._save_data()

    def reset(self):
        self.data.setdefault(self.user_id, {})[self.resource_name] = 0
        self._save_data()
        
    def set_property(self, property_name, value):
        user_data = self.data.setdefault(self.user_id, {})
        user_data[property_name] = value
        self._save_data()

    def get_property(self, property_name):
        return self.data.get(self.user_id, {}).get(property_name)