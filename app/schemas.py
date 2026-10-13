from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .db import today

class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Details(StrictModel):
    appliance: Literal['fan','refrigerator','washing_machine'] | None = None
    zone: Literal['north','central','south'] | None = None
    preferred_date: date | None = None
    time_preference: Literal['any','morning','afternoon'] = 'any'
    max_visit_fee: int | None = Field(default=None, ge=0, le=100000, strict=True)
    issue_description: str | None = Field(default=None, max_length=500)

    @field_validator('preferred_date')
    @classmethod
    def valid_date(cls, value):
        if value and not 1 <= (value-today()).days <= 14:
            raise ValueError('Choose a date from tomorrow through the next 14 days')
        return value

class Change(Details):
    revision: int = Field(ge=0)

class Selection(StrictModel):
    slot_id: int = Field(gt=0)
    revision: int = Field(ge=0)

class Confirmation(Selection):
    request_id: str = Field(min_length=8,max_length=100,pattern=r'^[A-Za-z0-9_-]+$')
    confirmed: Literal[True]

class Chat(StrictModel):
    text: str = Field(min_length=1,max_length=2000)
    revision: int = Field(ge=0)

class Access(StrictModel):
    access_code: str = Field(default='',max_length=200)

class Plan(StrictModel):
    action: Literal['update','options','select','resume','help'] = 'help'
    changes: Details = Field(default_factory=Details)
    option_number: int | None = Field(default=None,ge=1,le=3)
