from qual.core.xyapi.database.sqlalchemy_activerecord import Model
from qual.apps.user.model import User
from qual.apps.dictionary.model import Dictionary, Type, DictionaryKeyValue


def seed_user():
    if not User.is_empty_table():
        return

    admin = User(username="admin", display_name="admin")
    admin.set_password("admin")
    admin.save()


def seed_dictionary():
    if not Dictionary.is_empty_table():
        return

    account_type = Dictionary(key="account_type", name="账号类型", type=Type.text)
    account_local = DictionaryKeyValue(name="本地账户", value="本地账户", type=Type.text)
    account_xysso = DictionaryKeyValue(name="XYSSO账户", value="XYSSO账户", type=Type.text)
    account_type.children.append(account_local)
    account_type.children.append(account_xysso)
    account_type.save()

    switch = Dictionary(key="switch", name="开关", type=Type.boolean)
    switch_enable = DictionaryKeyValue(name="启用", value="true")
    switch_disable = DictionaryKeyValue(name="禁用", value="false")
    switch.children.append(switch_enable)
    switch.children.append(switch_disable)
    switch.save()


def seed():
    with Model.start_session(True):
        seed_user()
        seed_dictionary()
