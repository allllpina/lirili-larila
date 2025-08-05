from abc import ABC, abstractmethod

class JSON_interface(ABC):
    @abstractmethod
    def parse_dict(self, template: dict):
        """Parse dictionary to object fields"""
        pass
    
    @abstractmethod
    def dump_to_dict(self) -> dict:
        """Serialize object fields do dictionary"""
        pass


