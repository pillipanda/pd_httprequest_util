from pd_httprequest_util.request import Request
from pd_httprequest_util.connection.sync_ import SyncHttp
from pd_httprequest_util.request_manager import SyncRequestManager

from demos.config import valid_url, invalid_url


def main():
    manager = SyncRequestManager(parral_amount=2, cancel_if_fail=True)

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
    print(resp, type(resp), error)
    connection.close()


if __name__ == '__main__':
    main()
