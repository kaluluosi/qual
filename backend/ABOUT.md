# Qual 是一个xinyuan的一个通用web RESTFUL 后端模板

这段描述是读取自 `ABOUT.md`

Qual不考虑前后端融合，不支持 Session 。只支持基于JWT的认证。拿到了Token就等同于认证通过。

Qual默认提供了 `OAuth2PasswordBearer` 和 `XYSSO` 两种认证登录方式。这两种登录方式最终都是获取
JWT访问令牌，然后用访问令牌来实现前端登录。

授权、认证、注册方面有提供接口，但是没有提供登出接口。因为前端想要登出，只需要将前端保存的Token清理掉就可以了。

