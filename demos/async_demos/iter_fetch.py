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
