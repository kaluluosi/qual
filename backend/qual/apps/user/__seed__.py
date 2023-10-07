"""
NOTE: 种子数据的创建应该遵循以下原则

1. 只新增，不允许修改和删除
2. 已经存在就不填充
3. 始终确保种子数据不违反任何数据库约束。
4. 使用 `first_or_create` 避免重复条目。

系统运行依赖数据存在，而不依赖数据正确。已经存在的数据行如果新增了字段应该由
`Alembic` 的字段默认值迁移来解决问题。

另外需要测试完`seed`后才在生产环境部署。 
"""

from .dao import DAO
from .schema import UserCreate
from qual.core.xyapi.database.sqlalchemy import create_session

with create_session() as session:
    dao = DAO(session)

    dao.first_or_create(
        UserCreate(username="admin", display_name="admin", password="admin")
    )
