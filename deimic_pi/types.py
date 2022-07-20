import enum

import click


class DeimicComponentType(str, enum.Enum):
    OUTPUT = "O"
    INPUT = "I"


class Port(int, click.ParamType):
    MIN_NUMBER = 1
    MAX_NUMBER = 65535
    name = 'PORT'

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        return cls.convert(value)

    @classmethod
    def convert(cls, value, *args, **kwargs):
        if 1 <= (value := int(value)) <= cls.MAX_NUMBER:
            return int(value)
        return ValueError(f"Given value is out of range ({cls.MIN_NUMBER} - {cls.MAX_NUMBER})")
