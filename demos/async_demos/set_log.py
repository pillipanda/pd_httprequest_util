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
