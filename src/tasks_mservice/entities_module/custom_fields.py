from datetime import datetime

from entities_module.interfaces import JSON_interface

custom_fields = {}  # Class registry


def register_class(name: str):
    """Class registry decorator"""

    def wrapper(cls: CustomField):
        custom_fields[name] = cls
        return cls

    return wrapper


class CustomField(JSON_interface):
    __necessary_keys__: dict[str, type]

    def __init__(self, template: dict):
        super().__init__()
        self.type: str
        self.parse_dict(template)

    def parse_dict(self, template):
        if self.check_template(
            template=template, necessary_keys=self.__necessary_keys__
        ):
            for key, type in self.__necessary_keys__.items():
                value = template[key]
                if isinstance(value, type):
                    setattr(self, key, value)
                else:
                    raise TypeError(
                        "[ERR] {} has wrong type: expected {}, got {}!"
                        .format(self.__class__.__name__, type, type(value))
                    )
        else:
            raise ValueError(
                "[Err] {} got a wrong template!"
                .format(self.__class__.__name__)
            )

    def dump_to_dict(self):
        return self.__dict__

    def check_template(self, template: dict, necessary_keys: list):
        """Method which checks if template has a valid structure"""
        for key in necessary_keys:
            if key not in template.keys():
                return False
        return True


# {"class": "deadline_date"}
@register_class("deadline_date")
class Deadline(CustomField):
    """Deadline that takes dict template as follows:
    {'type': 'deadline', 'date': str, 'is_expired': bool}"""

    __necessary_keys__: dict[str, type] = {"date": str, "is_expired": bool}

    def __init__(self, template):
        super().__init__(template)
        self.type = "deadline_date"

    def parse_dict(self, template):
        """CustomField.parse_dict() overloading
        for realization computing field"""
        if self.check_template(
            template=template, necessary_keys=Deadline.__necessary_keys__
        ):
            self.date = template["date"]
            self.is_expired = self.expiration_check()
        else:
            raise ValueError(
                "[Err] {} got a wrong template!"
                .format(self.__class__.__name__)
            )

    def expiration_check(self) -> bool:
        """Method that matches current date and deadline date"""
        return (
            datetime.strptime(
                self.date,
                "%d-%m-%Y %H:%M:%S"
            )
            < datetime.now()
        )


# {"class": "checkbox"}
@register_class("checkbox")
class Checkbox(CustomField):
    """Checkbox that takes dict template as follows:
    {'type': 'checkbox', 'checked': bool, 'text': str}
    """

    __necessary_keys__: dict[str, type] = {"checked": bool, "text": str}

    def __init__(self, template):
        super().__init__(template)
        self.type = "checkbox"


# {"class": "text"}
@register_class("text")
class Text(CustomField):
    """Text that takes dict template as follows:
    {'type': 'text', 'text': str}"""

    __necessary_keys__: dict[str, type] = {"text": str}

    def __init__(self, template):
        super().__init__(template)
        self.type = "text"


# {"class": "dropdown"}
@register_class("dropdown")
class Dropdown(CustomField):
    """Dropdown that takes dict template as follows:
    {'type': 'dropdown', 'elements': list[str], 'index_of_selected': int}"""

    __necessary_keys__: dict[str, type] = {
        "elements": list[str],
        "index_of_selected": int,
    }

    def __init__(self, template):
        super().__init__(template)
        self.type = "dropdown"
