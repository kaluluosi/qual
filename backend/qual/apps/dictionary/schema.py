from pydantic import BaseModel, ConfigDict
from .model import Type


class DictionaryBase(BaseModel):
    key: str
    name: str
    type: int = Type.text
    enable: bool = True
    sort: int = 1
    comment: str = ""


class DictionaryRead(DictionaryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class DictionaryKeyValueRead(BaseModel):
    id: int
    name: str
    value: str
    type: int
    enable: bool
    sort: int
    parent_id: int

    model_config = ConfigDict(from_attributes=True)


class DictionaryReadDetial(DictionaryRead):
    children: list[DictionaryKeyValueRead]


class DictionaryCreate(DictionaryBase):
    ...


class DictionaryUpdate(DictionaryBase):
    ...


class DcitionaryKeyValueCreate(BaseModel):
    name: str
    value: str
    type: int
    enable: bool
    sort: int

    model_config = ConfigDict(from_attributes=True)
