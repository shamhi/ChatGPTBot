from ..basestorage.storage import MultipleQueryResults, RawConnection, SingleQueryResult
from typing import Any, Optional, TypeVar
from datetime import datetime
import structlog
import asyncpg
import json
import time


T = TypeVar("T")


class PostgresConnection(RawConnection):
    def __init__(
        self,
        connection_poll: asyncpg.Pool,
        logger: structlog.typing.FilteringBoundLogger,
    ):
        self._pool = connection_poll

        self._logger = logger

    async def _fetch(
        self,
        sql: str,
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]] = None,
        con: Optional[asyncpg.Connection] = None,
    ) -> MultipleQueryResults:
        st = time.monotonic()
        request_logger = self._logger.bind(sql=sql, params=params)
        request_logger.debug("Making query to DB")
        try:
            if con is None:
                async with self._pool.acquire() as con:
                    if params is not None:
                        raw_result = await con.fetch(sql, *params)
                    else:
                        raw_result = await con.fetch(sql)
            else:
                if params is not None:
                    raw_result = await con.fetch(sql, *params)
                else:
                    raw_result = await con.fetch(sql)
        except Exception as e:
            # change to appropriate error handling
            request_logger = request_logger.bind(error=e)
            request_logger.error(f"Error while making query: {e}")
            raise e
        else:
            results = [i for i in raw_result]
        finally:
            request_logger.debug(
                "Finished query to DB", spent_time_ms=(time.monotonic() - st) * 1000
            )

        return MultipleQueryResults(results)

    async def _fetchrow(
        self,
        sql: str,
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]] = None,
        con: Optional[asyncpg.Connection] = None,
    ) -> SingleQueryResult:
        st = time.monotonic()
        request_logger = self._logger.bind(sql=sql, params=params)
        request_logger.debug("Making query to DB")

        try:
            if con is None:
                async with self._pool.acquire() as con:
                    if params is not None:
                        raw = await con.fetchrow(sql, *params)
                    else:
                        raw = await con.fetchrow(sql)
            else:
                if params is not None:
                    raw = await con.fetchrow(sql, *params)
                else:
                    raw = await con.fetchrow(sql)
        except Exception as e:
            request_logger = request_logger.bind(error=e)
            request_logger.error(f"Error while making query: {e}")
            raise e
        else:
            result = raw
        finally:
            request_logger.debug(
                "Finished query to DB", spent_time_ms=(time.monotonic() - st) * 1000
            )

        return SingleQueryResult(result)

    async def _execute(
        self,
        sql: str,
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]] = None,
        con: Optional[asyncpg.Connection] = None,
    ) -> None:
        st = time.monotonic()
        request_logger = self._logger.bind(sql=sql, params=params)
        request_logger.debug("Making query to DB")
        try:
            if con is None:
                async with self._pool.acquire() as con:
                    if params is not None:
                        if isinstance(params, list):
                            await con.executemany(sql, params)
                        else:
                            await con.execute(sql, *params)
                    else:
                        await con.execute(sql)
            else:
                if params is not None:
                    if isinstance(params, list):
                        await con.executemany(sql, params)
                    else:
                        await con.execute(sql, *params)
                else:
                    await con.execute(sql)
        except Exception as e:
            # change to appropriate error handling
            request_logger = self._logger.bind(error=e)
            request_logger.error(f"Error while making query: {e}")
            raise e
        finally:
            request_logger.debug(
                "Finished query to DB", spent_time_ms=(time.monotonic() - st) * 1000
            )

    async def create_main_table(self) -> None:
        sql = """CREATE TABLE IF NOT EXISTS users(
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        user_name VARCHAR(32),
                        history JSONB,
                        registered_at TIMESTAMP)"""

        await self._execute(sql)

    async def register_user(self, user_id: int, name: str) -> None:
        check_user = await self._fetchrow(sql='SELECT * FROM users WHERE user_id = $1', params=(user_id,))

        if not check_user.data:
            sql = "INSERT INTO users (user_id, user_name, history, registered_at) VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING"
            params = (
                user_id,
                name,
                json.dumps([]),
                datetime.now(),
            )
            await self._execute(sql, params)

    async def add_message_to_history(self, history_dict: dict[str, str], user_id: int):
        current_history = await self._execute(f"SELECT history FROM users WHERE user_id = {user_id}")

        history_list = json.loads(current_history) if current_history else []
        history_list.append(history_dict)

        updated_history = json.dumps(history_list)

        sql = "UPDATE users SET history = $1 WHERE user_id = $2"
        params = (updated_history, user_id)

        await self._execute(sql, params)

    async def get_users_columns(self):
        sql = "SELECT * FROM users"
        result = await self._fetch(sql)
        return result.data
