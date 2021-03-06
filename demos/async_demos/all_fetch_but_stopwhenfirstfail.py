from pd_httprequest_util.request import Request
from pd_httprequest_util.connection.async_ import AsyncConnection
from pd_httprequest_util.request_manager import AsyncRequestManager

from demos.config import valid_url, invalid_url


async def main():
    # 这里通过设置cancel_if_fail=True参数使得第一个失败便返回
    manager = AsyncRequestManager(parral_amount=2, cancel_if_fail=True)

    connection = await AsyncConnection.create()
    for i in range(10):
        url = valid_url
        if i == 5: url = invalid_url
        request = Request(
            http_conn=connection,
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
