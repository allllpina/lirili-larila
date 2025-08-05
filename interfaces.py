from abc import ABC, abstractmethod

class JSON_interface(ABC):
    @abstractmethod
    def parse_dict(self, template: dict) -> None:
        """Parse dictionary to object fields"""
        pass
    
    @abstractmethod
    def dump_to_dict(self) -> dict:
        """Serialize object fields do dictionary"""
        pass

    @abstractmethod
    def check_template(self, template: dict) -> bool:
        """Check if all fields that needed is in template"""
        pass
