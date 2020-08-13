from pd_httprequest_util.request import Request
from pd_httprequest_util.connection.async_ import AsyncHttp
from pd_httprequest_util.request_manager import AsyncRequestManager

from demos.config import valid_url, invalid_url

async def main():
    # 此批访问的并发数为60, 失败request的返回空字符串
    manager = AsyncRequestManager(parral_amount=60, fail_return='')

    # 此批访问全部服用此connection
    connection = await AsyncHttp.create()

    # 构建100个请求、其中第五个故意设置为无效的url
    for i in range(100):
        url = valid_url
        if i == 5: url = invalid_url
        request = Request(
            http_req=connection,
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
