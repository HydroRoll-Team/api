import asyncio
from enum import Enum

import aiohttp

from fastapi import status


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    # PUT = "PUT"
    # DELETE = "DELETE"
    # PATCH = "PATCH"


class HttpRequestResult:
    url: str = None
    content: str = None
    status_code: status = None

    def __init__(self,
                 url: str,
                 content: str = None,
                 status_code: status = status.HTTP_200_OK):
        self.url = url
        self.content = content
        self.status_code = status_code

    def add_error(self,
                  message: str = None,
                  status_code: status = status.HTTP_400_BAD_REQUEST):
        self.status_code = status_code
        if message is None:
            self.content["message"] = "It is not an error from the Hydroroll server, " + \
                " but the request did not return a 200 response." + \
                " Please check the URL and try again."
        else:
            self.content["message"] = message


class ContentType(Enum):
    JSON = "application/json"
    HTML = "text/html"


async def http_request(
        url: str,
        method: HttpMethod,
        content_type: ContentType = ContentType.JSON,
        limit: int = 10,
        timeout: int = 1,
        verify_ssl: bool = True) -> HttpRequestResult:
    """
    Make a http request with a semaphore and timeout

    Args:
        url (str): The url to request
        method (HttpMethod): The method to use
        content_type (ContentType): The content type to expect(default: ContentType.JSON)
        limit (int): The limit of concurrent requests(default: 10)
        timeout (int): The timeout for the request in seconds(default: 1)
        verify_ssl (bool): Whether to verify the SSL certificate(default: True)
    """

    result = HttpRequestResult(url=url)

    semaphore = asyncio.Semaphore(limit)
    timeout = aiohttp.ClientTimeout(total=timeout)

    conn = aiohttp.TCPConnector(verify_ssl=verify_ssl)
    async with (semaphore):
        try:
            async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
                async with session.request(method=method.value, url=url) as resp:

                    if not resp.ok:
                        result.add_error(status_code=resp.status)
                        return result

                    if content_type == ContentType.JSON:
                        result.content = await resp.json()
                    elif content_type == ContentType.HTML:
                        result.content = await resp.text()
                    return result

        except aiohttp.ClientConnectorError as e:
            result.add_error(status_code=status.HTTP_502_BAD_GATEWAY)
            return result

        except asyncio.TimeoutError as e:
            result.add_error(
                status_code=status.HTTP_408_REQUEST_TIMEOUT, message=str(e))
            return result

        except Exception as e:
            result.add_error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
            return result
