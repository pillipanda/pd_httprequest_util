from pd_httprequest_util.request import Request
from pd_httprequest_util.connection.sync_ import SyncHttp
from pd_httprequest_util.request_manager import SyncRequestManager

from demos.config import valid_url, invalid_url

def main():
    manager = SyncRequestManager(parral_amount=4)

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

    cursor_resp = manager.visit_iter()
    for resp in cursor_resp:
        print('suc' if len(resp) > 0 else 'fail')
    connection.close()


if __name__ == '__main__':
    main()
