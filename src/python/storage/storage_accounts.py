from pathlib import Path
from src.python.storage.storage_master import JSONStoreMaster

class JSONStoreAccounts(JSONStoreMaster):
    """Almacenamiento para usuarios"""
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    _FILE_PATH = project_root / "json_storage" / "users.json"
    _data_list = []