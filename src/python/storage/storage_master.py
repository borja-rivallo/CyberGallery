import json
from pathlib import Path
from src.python.main.exception_management import ExceptionManagement

class JSONStoreMaster():
    """Superclase de la que derivarán todas las dedicadas al almacenamiento y lectura de datos"""
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    _FILE_PATH = project_root / "json_storage" / "artwork.json"
    _data_list = []

    def __init__(self):
        self.read_store()
    

    def read_store(self):
        """Función para leer el contenido del JSON"""
        try:
            with open(self._FILE_PATH, "r", encoding="utf-8", newline="") as file:
                data = json.load(file)
                if isinstance(data, list):
                    self._data_list = data
                    return self._data_list
                else:
                    self._data_list = []
                    return self._data_list

        except FileNotFoundError:
            self._data_list = []
            return self._data_list
        except json.JSONDecodeError as ex:
            raise ExceptionManagement("JSON Decode Error - Wrong JSON Format") from ex

    def save_store(self):
        """Función para guardar en el JSON"""
        try:
            with open(self._FILE_PATH, "w", encoding="utf-8", newline="") as file:
                json.dump(self._data_list, file, indent=2)
        except FileNotFoundError as ex:
            raise ExceptionManagement("Wrong file  or file path") from ex
        except json.JSONDecodeError as ex:
            raise ExceptionManagement("JSON Decode Error - Wrong JSON Format") from ex

    def add_item(self, item):
        """Función para añadir objetos al JSON"""
        self._data_list.append(item)
        self.save_store()
