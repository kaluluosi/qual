from fastapi import APIRouter, status
from qual.core.xyapi.exception import NotFoundError
from .model import Dictionary, DictionaryKeyValue
from .schema import (
    DictionaryReadDetial,
    DictionaryCreate,
    DictionaryUpdate,
    DictionaryKeyValueRead,
    DcitionaryKeyValueCreate,
)


api = APIRouter(prefix="/dict", tags=["dict"])


@api.get("", response_model=list[DictionaryReadDetial])
async def get_dicts():
    dicts = Dictionary.scalars(Dictionary.select.where()).all()
    return dicts


@api.get("/{key}", response_model=DictionaryReadDetial)
async def get_dict(key: str):
    _dict = Dictionary.get_by_key(key)
    if _dict:
        return _dict
    else:
        raise NotFoundError(f"key={key}的字典不存在")


@api.post("", status_code=status.HTTP_201_CREATED)
async def add_dict(dict_c: DictionaryCreate):
    _dict = Dictionary(**dict_c.model_dump())
    _dict.save()


@api.patch("/{key}")
async def update_dict(key: str, dict_u: DictionaryUpdate):
    """
    更新已存在的字典
    """
    _dict = Dictionary.get_by_key(key)
    if _dict:
        _dict.update(**dict_u.model_dump())
    else:
        raise NotFoundError(f"key={key}的字典不存在")


@api.delete("/{key}")
async def delete_dict(key: str):
    _dict = Dictionary.get_by_key(key)
    if _dict:
        _dict.delete()
    else:
        raise NotFoundError(f"key={key}的字典不存在")


@api.get("/{key}/values", response_model=list[DictionaryKeyValueRead])
async def get_dict_values(key: str):
    _dict = Dictionary.get_by_key(key)
    if _dict:
        return _dict.children
    else:
        raise NotFoundError(f"key={key}的字典不存在")


@api.post("/{key}/values")
async def add_dict_values(key: str, dict_value_c: DcitionaryKeyValueCreate):
    _dict = Dictionary.get_by_key(key)

    if _dict:
        value = DictionaryKeyValue(**dict_value_c.model_dump())
        _dict.children.append(value)
        _dict.save()

    else:
        raise NotFoundError(f"key={key}的字典不存在")


@api.get("/{key}/values/{id}", response_model=DictionaryKeyValueRead)
async def get_dict_value(key: str, id: int):
    stmt = (
        DictionaryKeyValue.select.select_from(Dictionary)
        .join(DictionaryKeyValue.parent)
        .where(Dictionary.key == key)
    )

    value = DictionaryKeyValue.scalar(stmt)
    return value


@api.delete("/{key}/values/{id}")
async def delete_dict_values(key: str, id: int):
    stmt = DictionaryKeyValue.select.where(
        DictionaryKeyValue.parent.has(Dictionary.key == key),
        DictionaryKeyValue.id == id,
    )

    value = DictionaryKeyValue.scalar(stmt)
    if value:
        value.delete()
    else:
        raise NotFoundError("字典值不存在")
