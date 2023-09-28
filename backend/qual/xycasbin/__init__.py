import casbin
import pkg_resources

model_conf = pkg_resources.resource_filename(__package__, "model.conf")  # 模型配置
policy = pkg_resources.resource_filename(__package__, "policy")  # 规则/适配器

e = casbin.Enforcer(model=model_conf, adapter=policy)
