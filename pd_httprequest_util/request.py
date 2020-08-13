import sys
import asyncio
import traceback
from typing import Optional
from datetime import datetime
from dataclasses import dataclass

import aiohttp
import requests

from pd_httprequest_util.utils.log_util import LoggerUtil
from pd_httprequest_util.connection import HttpReqer


@dataclass
class Request:
    http_req: HttpReqer

    url: str = ''
    method: str = ''

    params: Optional[dict] = None
    post_data: Optional[dict] = None
    headers: Optional[dict] = None
    is_json: bool = False
    timeout: int = 100

    no_retry: bool = False

    log_flag: str = ''  # only set it when u need log & distinguish between requests

    @staticmethod
    async def req_all(async_tasks_list: []):
        if not async_tasks_list: return []

    async def async_req(self, logger_ins: Optional[LoggerUtil] = None) -> str:
        """
        :param logger_ins: 如果传入空表示不记录日志
        :return: decoded resp body
        """
        kwargs = {
            'params': self.params,
            'headers': self.headers,
            'timeout': self.timeout,
            'verify_ssl': False,
        }
        if logger_ins:
            kwargs['trace_request_ctx'] = type(sys.implementation)(flag=self.log_flag,
                                                                   logger=logger_ins)
        if self.is_json and self.post_data:
            kwargs['json'] = self.post_data
        elif not self.is_json and self.post_data:
            kwargs['data'] = self.post_data

        try_time = 0
        while try_time < 2:
            try:
                resp = await aiohttp.client._RequestContextManager(
                    self.http_req.session._request(
                        self.method,
                        self.url,
                        **kwargs
                    )
                )
                if resp.status >= 400: raise Exception(f'http_status:{resp.status}')
            except asyncio.TimeoutError:
                try_time += 1
                if self.no_retry: return ''
                if not logger_ins: continue
                logger_ins.warning(
                    f'flag:{self.log_flag}|spend:{self.timeout}|context:{self.method}-{self.url}-{self.is_json}-{kwargs}|error:Timeout of {self.timeout}s|error_detail:'
                )
            except Exception as e:
                try_time += 1
                if self.no_retry: return ''
                traceback_str = traceback.format_exc().replace('\n', '\t')
                await self.http_req.change_conn()
                if not logger_ins: continue
                traceback_str = traceback.format_exc().replace('\n', '\t')
                logger_ins.warning(
                    f'flag:{self.log_flag}|spend:{self.timeout}|context:{self.method}-{self.url}-{self.is_json}-{kwargs}|error:Timeout of {self.timeout}s|error_detail:{traceback_str}'
                )
            else:
                resp = await resp.text()
                return resp

        # 第三次新起session进行尝试, 并且立即关闭
        if not kwargs['headers']:
            kwargs['headers'] = {"connection": "close"}
        else:
            kwargs['headers'].update({"connection": "close"})
        async with aiohttp.ClientSession() as session:
            try:
                resp = await aiohttp.client._RequestContextManager(
                    session._request(self.method, self.url, **kwargs)
                )
                if resp.status >= 400: raise Exception(
                    f'status code fail: {resp.status}')
                resp = await resp.text()
            except:
                traceback_str = traceback.format_exc().replace('\n', '\t')
                return ''
            else:
                return resp
        return ''

    def sync_req(self, logger_ins: Optional[LoggerUtil] = None) -> str:
        if self.method not in aiohttp.hdrs.METH_ALL:
            error = f'http method {self.method} not in {aiohttp.hdrs.METH_ALL}'
            return ''

        kwargs = {
            'params': self.params,
            'headers': self.headers,
            'timeout': self.timeout,
        }
        if self.is_json and self.post_data:
            kwargs['json'] = self.post_data
        elif not self.is_json and self.post_data:
            kwargs['data'] = self.post_data

        try_time = 0
        while try_time < 2:
            start = datetime.now()
            try:
                resp = self.http_req.session.request(method=self.method,
                                                     url=self.url,
                                                     **kwargs).text
            except requests.Timeout:
                try_time += 1
                if logger_ins:
                    gap = (datetime.now() - start).microseconds/1000
                    logger_ins.warning(
                        f'flag:{self.log_flag}|spend:{gap}|context:{self.method}-{self.url}-{self.is_json}-{kwargs}|error:Timeout of {self.timeout}s|error_detail:'
                    )
                if self.no_retry: return ''
            except:
                try_time += 1
                if logger_ins:
                    gap = (datetime.now() - start).microseconds/1000
                    logger_ins.warning(
                        f'flag:{self.log_flag}|spend:{gap}|context:{self.method}-{self.url}-{self.is_json}-{kwargs}|error:|error_detail:{traceback}'
                    )
                if self.no_retry: return ''
            else:
                if logger_ins:
                    gap = (datetime.now() - start).microseconds/1000
                    logger_ins.info(f'flag:{self.log_flag}|spend:{gap}|context:|error:|error_detail:')
                return resp

        # 第三次新起session进行尝试, 并且立即关闭
        if not kwargs['headers']:
            kwargs['headers'] = {"connection": "close"}
        else:
            kwargs['headers'].update({"connection": "close"})
            try:
                resp = requests.request(method=self.method, url=self.url,
                                        **kwargs).text
            except:
                traceback_str = traceback.format_exc().replace('\n', '\t')
                return ''
            else:
                return resp

        return ''
