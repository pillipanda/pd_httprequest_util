import asyncio

from aiohttp import ClientSession, TCPConnector, TraceConfig

from pd_httprequest_util.connection.main import HttpReqer


class AsyncHttp(HttpReqer):
    @classmethod
    async def create(cls, conn_total_limit=1000, limit_per_host=0):
        self = cls()
        self.limit = conn_total_limit
        self.limit_per_host = limit_per_host

        conn = TCPConnector(limit=self.limit, limit_per_host=self.limit_per_host)
        self._session = await ClientSession(trace_configs=[http_trace_config()],
                                            connector=conn).__aenter__()
        return self

    @property
    def session(self):
        return self._session

    async def change_conn(self):
        if not self._session.closed: return
        asyncio.ensure_future(self._close_session(self._session))
        await self.close()
        new_ins = await AsyncHttp.create(conn_total_limit=self.limit, limit_per_host=self.limit_per_host)
        self._session = new_ins.session

    def close(self):
        asyncio.ensure_future(self._session.close())

    @staticmethod
    async def _close_session(session):
        asyncio.ensure_future(session.close())


def http_trace_config():
    async def _on_request_start(session, trace_config_ctx, params):
        if not trace_config_ctx.trace_request_ctx: return
        trace_config_ctx.trace_request_ctx.start = session.loop.time()

    async def _on_request_end(session, trace_config_ctx, params):
        if not trace_config_ctx.trace_request_ctx: return
        elapsed = round((session.loop.time() - trace_config_ctx.trace_request_ctx.start)*1000, 3)
        trace_config_ctx.trace_request_ctx.logger.info(
            f"flag:{trace_config_ctx.trace_request_ctx.flag}|spend:{elapsed}|context:|error:|error_detail:"
        )

    trace_config = TraceConfig()
    trace_config.on_request_start.append(_on_request_start)
    trace_config.on_request_end.append(_on_request_end)
    return trace_config
