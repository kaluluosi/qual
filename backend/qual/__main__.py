from qual import serve


# 必须要用这个判断语句，不然导入qual的时候就执行起服务了，导致别人引用这个模块卡死
# 这个__main__的存在目的是为了用来在vscode中通过调试启动后端用
if __name__ == "__main__":
    serve()
