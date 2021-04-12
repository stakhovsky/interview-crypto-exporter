import asyncio
import typing

import backoff
import httpx
import orjson


class Response:
    __slots__ = (
        '_real',
    )

    def __init__(
        self,
        real: httpx.Response,
    ):
        self._real = real

    @property
    def code(self) -> int:
        return self._real.status_code

    @property
    def body(self) -> typing.Any:
        return self._real.read()

    @property
    def json(self) -> typing.Union[
        typing.Dict,
        typing.List[typing.Any],
    ]:
        return orjson.loads(self.body)


class Transport:
    __slots__ = (
        '_transport',
    )

    def __init__(
        self,
    ):
        self._transport = httpx.AsyncClient()

    @staticmethod
    def _build_retries(
        retries: typing.Optional[int] = None,
        retry_exceptions: typing.Optional[
            typing.Sequence[typing.Type[Exception]]
        ] = (),
        retry_condition: typing.Optional[
            typing.Callable[[Response], bool]
        ] = None,
    ) -> typing.Sequence[typing.Callable]:
        result = []
        if retries:
            if retry_exceptions is not None:
                result.append(backoff.on_exception(
                    wait_gen=backoff.expo,
                    max_tries=retries,
                    exception=tuple(retry_exceptions),
                ))
            if retry_condition is not None:
                result.append(backoff.on_predicate(
                    wait_gen=backoff.expo,
                    max_tries=retries,
                    predicate=retry_condition,
                ))
        return result

    async def _do_request(
        self,
        method: str,
        url: str,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        query: typing.Optional[typing.Dict[str, str]] = None,
        body: typing.Optional[typing.Union[
            bytes,
            str,
            typing.Dict[str, typing.Any],
            typing.List[typing.Any],
        ]] = None,
    ) -> Response:
        data_param = dict()
        if isinstance(body, (bytes, str)):
            data_param['data'] = body
        elif isinstance(body, (dict, list, tuple, set)):
            data_param['json'] = body
        real_response = await self._transport.request(
            method=method,
            url=url,
            headers=headers,
            params=query,
            **data_param,
        )
        return Response(
            real=real_response,
        )

    async def _request(
        self,
        method: str,
        url: str,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        query: typing.Optional[typing.Dict[str, str]] = None,
        body: typing.Optional[typing.Union[
            bytes,
            str,
            typing.Dict[str, typing.Any],
            typing.List[typing.Any],
        ]] = None,
        retries: typing.Optional[int] = None,
        retry_exceptions: typing.Optional[
            typing.Sequence[typing.Type[Exception]]
        ] = (),
        retry_condition: typing.Optional[
            typing.Callable[[Response], bool]
        ] = None,
    ) -> Response:
        retries_functions = self._build_retries(
            retries=retries,
            retry_exceptions=retry_exceptions,
            retry_condition=retry_condition,
        )

        request_fn = self._do_request
        for retry_fn in retries_functions:
            request_fn = retry_fn(request_fn)

        response: Response = await request_fn(
            method=method,
            url=url,
            headers=headers,
            query=query,
            body=body,
        )

        return response

    async def get(
        self,
        url: str,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        query: typing.Optional[typing.Dict[str, str]] = None,
        body: typing.Optional[typing.Union[
            bytes,
            str,
            typing.Dict[str, typing.Any],
            typing.List[typing.Any],
        ]] = None,
        retries: typing.Optional[int] = None,
        retry_exceptions: typing.Optional[
            typing.Sequence[typing.Type[Exception]]
        ] = (),
        retry_condition: typing.Optional[
            typing.Callable[[Response], bool]
        ] = None,
    ) -> Response:
        return await self._request(
            method='GET',
            url=url,
            headers=headers,
            query=query,
            body=body,
            retries=retries,
            retry_exceptions=retry_exceptions,
            retry_condition=retry_condition,
        )

    async def close(self) -> typing.NoReturn:
        if self._transport is not None:
            await self._transport.aclose()

    def __del__(self):
        asyncio.get_event_loop().create_task(self.close())


def join(
    pieces: typing.Sequence[str],
) -> str:
    result = ''
    for piece in pieces:
        result = f'{result.rstrip("/")}/{piece.lstrip("/")}'
    return result
