# -*- coding: utf-8 -*-

from threading import Thread


def async_run(f, *args, **kwargs):
    thread = Thread(target=f, args=args, kwargs=kwargs)
    # 设置 daemon 为 True 以使用户按 Ctrl + C 结束程序时，各子线程也能跟着结束
    # 不然会因为子线程不结束，而使得整个程序也无法结束
    # https://stackoverflow.com/a/11816038
    thread.daemon = True
    thread.start()
