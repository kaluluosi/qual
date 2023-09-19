from passlib.context import CryptContext

"""
密码的哈希和校验用passlib。
## 为什么不直接用 `bcrypt`或者其他具体的哈希库
1. passlib相当于是一个哈希管理器，可以配置使用多个哈希库。
2. passlib支持弃用，当弃用了一个哈希算法后，passlib会自动启用备选哈希算法，并且
提供方法来确认哈希密码是否需要更新（因为换了哈希算法，需要提醒用户更新密码）—— 迁移。

passlib相当于一个哈希密码层的作用。
"""

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    哈希密码

    Args:
        plain_password (str): 明文密码

    Returns:
        str: 哈希字符串
    """
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    校验密码

    Args:
        plain_password (str): 明文密码
        hashed_password (str): 哈希密码

    Returns:
        bool: 匹配返回 True，不匹配返回 False
    """
    return _pwd_context.verify(plain_password, hashed_password)
