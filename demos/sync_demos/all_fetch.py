from pd_httprequest_util.request import Request
from pd_httprequest_util.connection.sync_ import SyncConnection
from pd_httprequest_util.request_manager import SyncRequestManager

from demos.config import valid_url, invalid_url


def main():
    manager = SyncRequestManager(parral_amount=3, fail_return='')

    connection = SyncConnection.create()
    for i in range(10):
        url = valid_url
        if i == 5: url = invalid_url
        request = Request(
            http_conn=connection,
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
