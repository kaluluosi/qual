# DevContainer指南

## 什么是DevContainer（开发容器）

vscode的DevContainer相当于是在Docker中起一组容器，然后vscode连接到容器系统里做开发。
好处有以下：

无论团队成员是Windows、MacOS, 还是Linux，最终大家都是在同一个镜像创建的容器环境中开发，开发环境是一致的。
由于开发环境是在容器里，因此不会对宿主主机造成不必要的污染，不用安装各种环境工具数据库啥的。
比如 python，如果你宿主主机有 python 3.8是你常用的python版本，但是项目需要 python 3.11，那么你不需要折腾双版本pyhon和切换。
因为你是直接在容器里开发项目，用的是容器里的python。
如果项目需要数据库，你还要本地安装数据库和启动数据库服务。有了DevContainer只需要一个数据库容器即可，不用污染你的宿主主机。

## 通过开发容器打开项目后要做什么

开发容器只是配置好了环境，预安装了需要的工具，但是项目本身是没有初始化的。

### `backend` 项目

#### 初始化
`backend` 项目是 `python+poetry` 项目，要去 `backend` 目录执行 `poetry install` 安装依赖和创建虚拟环境。

ctrl+shift+\` 创建新终端，选择 `backend`。
命令行中执行

```shell
poetry install
```

然后打开一个python脚本，解析器选择刚才安装后创建的虚拟环境。


#### 调试

可以通过 `vscode` 调试工具，执行 `run dev(backend)` 来运行调试后端。

### `frontend`项目

#### 初始化

`frontend` 项目是 `vue+npm` 项目，那么你就要去 `frontend` 目录执行 `npm install` 安装依赖。

ctrl+shift+\` 创建新终端，选择 `frontend`。

命令行中执行

```shell
npm install
```

#### 调试

可以通过 `vscode` 调试工具，执行 `run dev(frontend)` 来运行调试前端。


## Git如何共享宿主的密钥

在容器里面的Git默认情况下是无法访问食用宿主主机的 ~/.ssh 下的密钥的。
宿主主机需要开启 `ssh-agent` 服务，然后通过 `ssh-add ~/.ssh/<你的私钥>` 的方式来讲私钥添加到ssh代理里。
这样容器里使用Git就可以访问到宿主的私钥了。

Windows下开启服务的方式是打开 `服务|services工具`，找到 `OpenSSH Authxxx` 服务，默认是禁用的，我们改为自动，然后手动启动。

然后调用 `ssh-add ~/.ssh/<你的私钥>` 将私钥添加到代理。这样进入开发容器后就可以用 Git 提交了。不然你就需要在容器里配置 `~/.ssh`了。