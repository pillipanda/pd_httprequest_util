import os
import asyncio
import concurrent.futures
from typing import Optional
from asyncio import FIRST_EXCEPTION

from pd_httprequest_util.request import Request
from pd_httprequest_util.utils.log_util import LoggerUtil
from pd_httprequest_util.utils.group_util import GroupHelper


class _RequestManager:
    logger = None

    def __init__(self,
                 parral_amount: int = 1000, *,
                 cancel_if_fail: bool = False,
                 fail_return=''):
        """
        :param parral_amount: 并发请求量
        :param cancel_if_fail: 是否此批量请求中如果存在>=1个失败的就cancel全部
        :param default_return: 对于不是有失败的就终止时、对于失败项的返回
        """
        assert isinstance(parral_amount, int), 'param parral_amount must be an Int'
        assert parral_amount > 0, 'param parral_amount must > 0'
        self.parral_amount = parral_amount

        self.cancel_if_fail = bool(cancel_if_fail)
        self.fail_return = fail_return

        self._request_tasks = []

    @classmethod
    def set_log(cls,
                name: str,
                dir_path: str, *,
                clear: bool = False,
                clear_days: Optional[int] = 60):
        if cls.logger is not None: return
        if not os.path.exists(dir_path):
            raise Exception(f'log dir path "{dir_path}" not exist')
        if clear and isinstance(clear_days, int):
            cls.logger = LoggerUtil(name, dir_path, clear_days).getLogger()
        else:
            cls.logger = LoggerUtil(name, dir_path).getLogger()

    def add_request(self, req: Request):
        self._request_tasks.append(req)


class AsyncRequestManager(_RequestManager):
    async def visit_all(self):
        grouped_requests = GroupHelper.group_by_items(self._request_tasks, self.parral_amount)

        ret = []
        for index, requests in enumerate(grouped_requests):
            coros = [i.async_req(logger_ins=self.logger) for i in requests]
            if self.cancel_if_fail:
                done, pending = await asyncio.wait(coros, return_when=FIRST_EXCEPTION)
                for pending_task in pending: pending_task.cancel()

                for done_task in done:
                    task_resp = done_task.result()
                    if not task_resp:
                        return [], 'get cancelled because of exist fail request'

                    ret.append(task_resp)
            else:
                resp = await asyncio.gather(*coros, return_exceptions=True)
                ret.extend([isinstance(i, str) and i or self.fail_return for i in resp])

        return ret, None

    async def visit_iter(self):
        grouped_requests = GroupHelper.group_by_items(self._request_tasks, self.parral_amount)

        for requests in grouped_requests:
            coros = [i.async_req(logger_ins=self.logger) for i in requests]
            resp = await asyncio.gather(*coros, return_exceptions=True)
            for i in resp:
                yield isinstance(i, str) and i or self.fail_return


class SyncRequestManager(_RequestManager):
    def visit_all(self):
        grouped_requests = GroupHelper.group_by_items(self._request_tasks, self.parral_amount)

        ret = []
        for requests in grouped_requests:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(i.sync_req, self.logger) for i in requests]
                for f in futures:
                    data = f.result()
                    if not data and self.cancel_if_fail:
                        return [], 'get cancelled because of exist fail request'
                    if not data and self.fail_return:
                        data = self.fail_return
                    ret.append(data)

        return ret, None

    def visit_iter(self):
        grouped_requests = GroupHelper.group_by_items(self._request_tasks, self.parral_amount)

        for requests in grouped_requests:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(i.sync_req, self.logger) for i in requests]
                for f in futures:
                    yield f.result()
