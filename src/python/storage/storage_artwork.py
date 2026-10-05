from pathlib import Path
from src.python.storage.storage_master import JSONStoreMaster

class JSONStoreArtworks(JSONStoreMaster):
    """Almacenamiento para obras de arte"""
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    _FILE_PATH = project_root / "json_storage" / "artworks.json"
    _data_list = []

    def find_by_id(self, artwork_id: str):
        """Busca una obra por su ID"""
        if not hasattr(self, '_data_list') or self._data_list is None:
            self._data_list = []
            
        for artwork in self._data_list:
            if artwork.get("artwork_id") == artwork_id:
                return artwork
        return None

    def find_by_owner(self, owner: str):
        """Busca obras por propietario"""
        return [artwork for artwork in self._data_list
                if artwork.get("owner") == owner]
    
    def delete_item_by_id(self, artwork_id: str) -> bool:
        """Elimina una obra por su ID"""
        initial_length = len(self._data_list)
        self._data_list = [artwork for artwork in self._data_list
                           if artwork.get("artwork_id") != artwork_id]
        if len(self._data_list) < initial_length:
            self.save_store()
            return True
        return False
