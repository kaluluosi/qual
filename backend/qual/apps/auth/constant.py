import enum


class Status(enum.StrEnum):
    active = "活动"
    inactive = "不活动"
    pending = "流程审批中"
    suspended = "暂停"
    closed = "关闭"


class AccountType(enum.StrEnum):
    local = "本地账户"
    ldap = "LDAP账户"
    xysso = "XYSSO账户"
    qywx = "企业微信账户"
