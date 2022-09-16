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
            return value
        raise ValueError(f"Given value is out of ports range ({cls.MIN_NUMBER} - {cls.MAX_NUMBER})")

    def __new__(cls, value):
        return cls.convert(value)
