### 特点
1. 支持设置并发数
2. 自动重试三次
3. 支持三种发送模式 
    1. 一次发起全部请求（应对请求数量不多的情况）
    2. 一次发起全部请求并当第一个出现失败时退出（应对请求数量不多&必须要全部成功的情况）
    3. iterator返回模式（应对请求数量太多、需要顾虑内存大小的情况）
4. 若connection出问题会自动切换
5. 同时支持同步/异步(async)调用方式
6. 支持打开日志记录每个请求的情况用于后续分析
7. 支持设定失败请求的默认返回值

### 概念说明
下面的使用例子会使用到Request、Connection、RequestManager三个类，先提前说明下其命名的逻辑：<br/>
每个具体http请求被命名为一个**Request**，其使用的http **Connection** pool是作为参数被依赖注入的，而外层使用RequestManager来管理一堆http request的访问特征

### 异步访问举例 <br/>
- 阻塞访问一批请求
```python
# 对应demos/async_demos/all_fetch.py
from pd_httprequest_util.request import Request
from pd_httprequest_util.connection.async_ import AsyncHttp
from pd_httprequest_util.request_manager import AsyncRequestManager

from demos.config import valid_url, invalid_url

async def main():
    # 此批访问的并发数为60, 失败request的返回空字符串
    manager = AsyncRequestManager(parral_amount=60, fail_return='')

    # 此批访问全部复用此connection
    connection = await AsyncHttp.create()

    # 构建100个请求、其中第五个故意设置为无效的url
    for i in range(100):
        url = valid_url
        if i == 5: url = invalid_url
        request = Request(
            http_req=connection,  # 依赖注入connection，多有request都复用此connection
            method='GET',
            url=url
        )
        manager.add_request(request)

    # 访问全部，resp: ['each resp text'], error
    resp, error = await manager.visit_all()
    suc, fail = 0, 0
    for i in resp:
        if len(i) > 0:
            suc += 1
        else:
            fail += 1
    print(suc, fail)
    assert fail == 1
    connection.close()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

```
-  阻塞访问一批请求，并在出现第一个失败request时便返回
```python
# 对应demos/async_demos/all_fetch_but_stopwhenfirstfail.py
from pd_httprequest_util.request import Request
from pd_httprequest_util.connection.async_ import AsyncHttp
from pd_httprequest_util.request_manager import AsyncRequestManager

from demos.config import valid_url, invalid_url


async def main():
    # 这里通过设置cancel_if_fail=True参数使得第一个失败便返回
    manager = AsyncRequestManager(parral_amount=2, cancel_if_fail=True)

    connection = await AsyncHttp.create()
    for i in range(10):
        url = valid_url
        if i == 5: url = invalid_url
        request = Request(
            http_req=connection,
            method='GET',
            url=url
        )
        manager.add_request(request)

    resp, error = await manager.visit_all()
    print(resp, type(resp), error)
    connection.close()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

- async iterator访问一批请求
```python
# 对应demos/async_demos/iter_fetch.py
from pd_httprequest_util.request import Request
from pd_httprequest_util.connection.async_ import AsyncHttp
from pd_httprequest_util.request_manager import AsyncRequestManager

from demos.config import valid_url, invalid_url

async def main():
    manager = AsyncRequestManager(parral_amount=4)

    connection = await AsyncHttp.create()
    for i in range(10):
        url = valid_url
        if i == 5: url = invalid_url   # a fail request
        request = Request(
            http_req=connection,
            method='GET',
            url=url
        )
        manager.add_request(request)

    # 这里，区别于阻塞的调用的是visit_all方法，此地调用visit_iter方法
    cursor_resp = manager.visit_iter()
    async for resp in cursor_resp:
        print('suc' if len(resp) > 0 else 'fail')
    connection.close()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

- 以"阻塞访问一批请求"为例，演示打开日志记录。余下同理
```python
# 对应demos/async_demos/set_log.py
from pd_httprequest_util.request import Request
from pd_httprequest_util.request_manager import AsyncRequestManager
from pd_httprequest_util.connection.async_ import AsyncHttp

async def main():
    manager = AsyncRequestManager(parral_amount=2)
    # 显式调用set_log方法，设置日志相关参数即打开了日志记录
    manager.set_log(
        name='http_request_log',
        dir_path='./',
        clear=True,
        clear_days=60
    )

    connection = await AsyncHttp.create()
    for i in range(10):
        url = 'http://httpbin.org/ip?whatever=1'
        if i == 5: url = 'http://web_not_exist.org/'   # a fail request
        request = Request(
            http_req=connection,
            method='GET',
            url=url,
            log_flag=f'req{i}',
        )
        manager.add_request(request)

    resp, error = await manager.visit_all()
    for i in resp:
        print('suc' if len(i) > 0 else 'fail')
    connection.close()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```


### 同步访问举例<br/>
**同步访问的核心就是把上面使用的AsyncRequestManager替换为SyncRequestManager,AsyncHttp替换为SyncHttp**
- 阻塞访问一批请求
```python
# 对应demos/sync_demos/all_fetch.py
from pd_httprequest_util.request import Request
from pd_httprequest_util.connection.sync_ import SyncHttp
from pd_httprequest_util.request_manager import SyncRequestManager

from demos.config import valid_url, invalid_url


def main():
    manager = SyncRequestManager(parral_amount=3, fail_return='')

    connection = SyncHttp.create()
    for i in range(10):
        url = valid_url
        if i == 5: url = invalid_url
        request = Request(
            http_req=connection,
            method='GET',
            url=url
        )
        manager.add_request(request)

    resp, error = manager.visit_all()
    for i in resp:
        print('-->', 'suc' if len(i) > 0 else 'fail')
    connection.close()


if __name__ == '__main__':
    main()
```
-  阻塞访问一批请求，并在出现第一个失败request时便返回
```python
# 对应demos/sync_demos/all_fetch_but_stopwhenfirstfail.py
...
```
-  iterator访问一批请求
```python
# 对应demos/sync_demos/iter_fetch.py
...
```
-  iterator访问一批请求
```python
# 对应demos/sync_demos/iter_fetch.py
...
```
- 设置日志
```python
# 对应demos/sync_demos/set_log.py
...
```
