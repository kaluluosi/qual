from qual.core.xyapi.database.sqlalchemy_activerecord import Model
from qual.apps.user.model import User
from qual.apps.dictionary.model import Dictionary, VariantType, DictionaryKeyValue


def seed_user():
    if not User.is_empty_table():
        return

    admin = User(username="admin", display_name="admin")
    admin.set_password("admin")
    admin.save()


def seed_dictionary():
    if not Dictionary.is_empty_table():
        return

    account_type = Dictionary(key="account_type", name="账号类型", type=VariantType.text)
    account_local = DictionaryKeyValue(name="本地账户", value="本地账户", type=VariantType.text)
    account_xysso = DictionaryKeyValue(
        name="XYSSO账户", value="XYSSO账户", type=VariantType.text
    )
    account_type.children.append(account_local)
    account_type.children.append(account_xysso)
    account_type.save()

    switch = Dictionary(key="switch", name="开关", type=VariantType.boolean)
    switch_enable = DictionaryKeyValue(name="启用", value="true")
    switch_disable = DictionaryKeyValue(name="禁用", value="false")
    switch.children.append(switch_enable)
    switch.children.append(switch_disable)
    switch.save()

    # Dictionary variantType
    variant_type = Dictionary(key="variant_type", name="值类型", type=VariantType.number)
    variant_text = DictionaryKeyValue(name="文本", value=VariantType.text)
    variant_number = DictionaryKeyValue(name="数值", value=VariantType.number)
    variant_date = DictionaryKeyValue(name="日期", value=VariantType.date)
    variant_datetime = DictionaryKeyValue(name="日期时间", value=VariantType.datetime)
    variant_time = DictionaryKeyValue(name="文本", value=VariantType.time)
    variant_file = DictionaryKeyValue(name="文件", value=VariantType.file)
    variant_boolean = DictionaryKeyValue(name="布尔", value=VariantType.boolean)
    variant_image = DictionaryKeyValue(name="图片", value=VariantType.image)
    variant_type.children.extend(
        [
            variant_text,
            variant_number,
            variant_date,
            variant_datetime,
            variant_time,
            variant_file,
            variant_boolean,
            variant_image,
        ]
    )
    variant_type.save()


def seed():
    with Model.start_session(True):
        seed_user()
        seed_dictionary()
