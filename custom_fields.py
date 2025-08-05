from interfaces import JSON_interface

custom_fields = {} # Class registry

def register_class(name: str):
    """Class registry decorator"""
    def wrapper(cls: CustomField):
        custom_fields[name] = cls
        return cls
    return wrapper


class CustomField(JSON_interface):

    def __init__(self, template: dict):
        super().__init__()

        self.parse_dict(template)

    def parse_dict(self, template: dict):
        pass

    def dump_to_dict(self):
        pass

    def check_template(self, template):
        pass


# {"class": "deadline_date"}
@register_class('deadline_date')
class Deadline(CustomField):
    def __init__(self, template):
        super().__init__(template)
        print(self.deadline_date)

    def parse_dict(self, template):
        date = template.get('date', None)
        if date is not None:
            self.deadline_date = date
        else:
            raise ValueError("Template has not a 'date' value")
        
    def is_expired(self) -> bool:
        pass


# {"class": "checkbox"}       
@register_class('checkbox')
class Checkbox(CustomField):
    pass


# {"class": "text"}
@register_class('text')
class Text(CustomField):
    pass


# {"class": "dropdown"}  
@register_class('dropdown')
class Dropdown(CustomField):
  pass