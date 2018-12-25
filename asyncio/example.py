import asyncio
import threading


# 在主线程中创建一个事件循环
loop = asyncio.new_event_loop()

# 设置当前线程的事件循环
asyncio.set_event_loop(loop)

# 获取当前运行事件循环， get_running_loop() 函数优于get_event_loop
loop = asyncio.get_running_loop()

# 将事件循环运行在子线程中
threading.Thread(target=loop.run_forever).start()

# asyncio.run_coroutine_threadsafe(coro, loop)
# Submit a coroutine to the given event loop. Thread-safe.
# Return a concurrent.futures.Future to wait for the result from another OS thread.
# 将coroutine协程对象提交给事件循环
asyncio.run_coroutine_threadsafe(main_work(), loop=loop)

# ensure_future 将 coroutine 封装成 future
# asyncio.ensure_future(coro_or_future, *, loop=None) If the argument is a Future, it is returned directly.
future = asyncio.ensure_future(somefunc(), loop=loop)
# task = loop.run_in_executor(executor=None, func=somefunc, *args)

# Wait for the single Future or coroutine object to complete with timeout. If timeout is None, block until the future completes.
await
asyncio.wait_for(fut, timeout, *, loop=None)

asyncio的协程是非抢占式的。协程如果不主动交出控制权，就会一直执行下去。
假如一个协程占用了太多时间，那么其他协程就有可能超时挂掉。

# --------------------------------主线程是同步的 - ------------------------------------ #

import time
import asyncio
from queue import Queue
from threading import Thread


def start_loop(loop):
    # 一个在后台永远运行的事件循环
    asyncio.set_event_loop(loop)
    loop.run_forever()


def do_sleep(x, queue, msg=""):
    time.sleep(x)
    queue.put(msg)


queue = Queue()

new_loop = asyncio.new_event_loop()

# 定义一个线程，并传入一个事件循环对象
t = Thread(target=start_loop, args=(new_loop,))
t.start()

print(time.ctime())

# 动态添加两个协程
# 这种方法，在主线程是同步的
new_loop.call_soon_threadsafe(do_sleep, 6, queue, "第一个")
new_loop.call_soon_threadsafe(do_sleep, 3, queue, "第二个")

while True:
    msg = queue.get()
    print("{} 协程运行完..".format(msg))
    print(time.ctime())

# 输出结果
Thu May 31 22:11:16 2018
第一个 协程运行完..
Thu May 31 22:11:22 2018
第二个 协程运行完..
Thu May 31 22:11:25 2018

# 总共耗时6+3=9秒.

--------------------------------主线程是异步的 - ------------------------------------
import time
import asyncio
from queue import Queue
from threading import Thread


def start_loop(loop):
    # 一个在后台永远运行的事件循环
    asyncio.set_event_loop(loop)
    loop.run_forever()


async def do_sleep(x, queue, msg=""):
    await
    asyncio.sleep(x)
    queue.put(msg)


queue = Queue()

new_loop = asyncio.new_event_loop()

# 定义一个线程，并传入一个事件循环对象
t = Thread(target=start_loop, args=(new_loop,))
t.start()

print(time.ctime())

# 动态添加两个协程
# 这种方法，在主线程是异步的
asyncio.run_coroutine_threadsafe(do_sleep(6, queue, "第一个"), new_loop)
asyncio.run_coroutine_threadsafe(do_sleep(3, queue, "第二个"), new_loop)

while True:
    msg = queue.get()
    print("{} 协程运行完..".format(msg))
    print(time.ctime())

# 输出结果
Thu May 31 22:23:35 2018
第二个 协程运行完..
Thu May 31 22:23:38 2018
第一个 协程运行完..
Thu May 31 22:23:41 2018

# 总共耗时max(6, 3)=6秒

# -----------------------------将事件循环运行在子线程中，在同步的主线程中调用(1) - -------------------------------- #
import threading
import asyncio

if __name__ == '__main__':
    # 创建一个事件循环loop
    loop = asyncio.new_event_loop()

    # 设置当前线程的事件循环
    asyncio.set_event_loop(loop)

    # 将事件循环运行在子线程中
    threading.Thread(target=loop.run_forever).start()

    async def main_work():
        while True:
            print('main on loop:%s' % id(loop))
            await
            asyncio.sleep(4)

    # asyncio.run_coroutine_threadsafe(coro, loop)
    # Submit a coroutine to the given event loop. Thread-safe.
    # Return a concurrent.futures.Future to wait for the result from another OS thread.
    # 将coroutine协程对象提交给事件循环
    asyncio.run_coroutine_threadsafe(main_work(), loop=loop)

    import time

    while (True):
        print("loop[%s] is running: %s" % (id(loop), loop.is_running()))
        time.sleep(2)

# -----------------------将事件循环运行在子线程中，在同步的主线程中调用(2) - 等价于(1) - --------------------------- #

import threading
import asyncio


def thread_loop_task(loop):
    # Run the event loop until stop() is called.
    # 运行事件循环，直到stop()调用
    loop.run_forever()


if __name__ == '__main__':

    # 创建一个事件循环thread_loop
    main_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main_loop)

    # 将thread_loop作为参数传递给子线程
    threading.Thread(target=thread_loop_task, args=(main_loop,)).start()

    async def main_work():
        while True:
            print('main on loop:%s' % id(main_loop))
            print("child threading id: %s" % threading.current_thread().ident)
            await
            asyncio.sleep(4)

    print("main threading id: %s" % threading.current_thread().ident)

    asyncio.run_coroutine_threadsafe(main_work(), loop=main_loop)

# --------------------------------子线程和主线程共用一个事件循环 - ------------------------------------ #

import threading
import asyncio


def thread_loop_task(loop):
    # 子线程和主线程公用一个事件循环
    async def work_2():
        while True:
            print('work_2 on loop:%s' % id(loop))
            await
            asyncio.sleep(2)

    async def work_4():
        while True:
            print('work_4 on loop:%s' % id(loop))
            await
            asyncio.sleep(4)

    asyncio.ensure_future(work_2(), loop=loop)
    asyncio.ensure_future(work_4(), loop=loop)


if __name__ == '__main__':

    # 创建一个事件循环thread_loop
    main_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main_loop)

    # 将thread_loop作为参数传递给子线程
    threading.Thread(target=thread_loop_task, args=(main_loop,)).start()

    async def main_work():
        while True:
            print('main on loop:%s' % id(main_loop))
            await
            asyncio.sleep(4)

    # Run until the future (an instance of Future) has completed.
    # 运行子线程和主线程公用的事件循环上的所有任务，直到完成
    main_loop.run_until_complete(main_work())

# --------------------------------子线程和主线程分别使用不同的事件循环 - ------------------------------------ #

import threading
import asyncio


def thread_loop_task(loop):
    # 为子线程设置自己的事件循环
    asyncio.set_event_loop(loop)

    async def work_2():
        while True:
            print('work_2 on loop:%s' % id(loop))
            await
            asyncio.sleep(2)

    async def work_4():
        while True:
            print('work_4 on loop:%s' % id(loop))
            await
            asyncio.sleep(4)

    future = asyncio.gather(work_2(), work_4())

    # Run until the future (an instance of Future) has completed.
    # 运行子线程中事件循环的所有任务，直到完成
    loop.run_until_complete(future)


if __name__ == '__main__':

    # 创建一个事件循环thread_loop
    thread_loop = asyncio.new_event_loop()

    # 将thread_loop作为参数传递给子线程
    threading.Thread(target=thread_loop_task, args=(thread_loop,)).start()

    # main_loop = asyncio.new_event_loop()
    # 不显试设置事件循环将获取默认的事件循环
    # asyncio.set_event_loop(main_loop)

    # 获取主线程的事件循环
    main_loop = asyncio.get_event_loop()


    async def main_work():
        while True:
            print('main on loop:%s' % id(main_loop))
            await
            asyncio.sleep(4)

    # Run until the future (an instance of Future) has completed.
    # 运行主线程中事件循环的所有任务，直到完成
    main_loop.run_until_complete(main_work())
