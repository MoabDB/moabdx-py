"""Take that stupid Intellisense, I do what I want!"""

from base64 import b64encode, b64decode
import requests

# pylint: disable=no-name-in-module
from .protocol_pb2 import Request as _Req, Response as _Response
from . import errors

# IPv6 address takes about 180 seconds to connect
# Dirty fix until a proper investigation is done
# Might break other code the user runs if connecting to IPv6
# pylint: disable=no-member
requests.packages.urllib3.util.connection.HAS_IPV6 = False

REQUEST = _Req
RESPONSE = _Response


def throw(res: _Response):
    """Throws appropriate errors for bad res codes"""
    if res.code == 200:
        pass
    elif res.code == 400:
        raise errors.MoabRequestError("Invalid request: " + res.message)
    elif res.code == 401:
        raise errors.MoabUnauthorizedError("Invalid credentials")
    elif res.code == 404:
        raise errors.MoabNotFoundError(res.message + " not found")
    elif res.code == 500:
        raise errors.MoabInternalError("Server error: " + res.message)
    else:
        raise errors.MoabResponseError(
            "Unknown error " + res.code + ": " + res.message)


setattr(_Response, "throw", throw)


def send(request: _Req, url) -> _Response:
    """
    Sends a request to the MoabDB API
    :param Request: The request to send
    :return: The response from the server
    """
    serialized_req = request.SerializeToString()
    headers = {
        'x-req': b64encode(serialized_req)
    }

    try:
        res = requests.get(url, headers=headers, timeout=180)

        if res.status_code == 429:
            raise errors.MoabRequestError("Too many requests")
        if res.status_code == 502:
            raise errors.MoabInternalError("Take2 server is down")
        if res.status_code != 200:
            raise errors.MoabHttpError("Unknown error")

        res = RESPONSE().FromString(b64decode(res.text))
        return res

    except requests.exceptions.Timeout as exc:
        raise errors.MoabHttpError("Connecting to server timed out") from exc


setattr(_Req, "send", send)
