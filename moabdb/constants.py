"""MoabDB Constants Manager"""
# pylint: disable=unused-import

from typing import Union
import io
import concurrent.futures as cf
import pandas as pd
from . import proto_wrapper


API_KEY = ""
API_USERNAME = ""
DB_URL = "https://api.moabdb.com/"

DAILY_COLUMNS = ['Symbol','Time','Open','High','Low','Close',\
                 'Volume','Trades','WgtdPrc','Bid','Ask']

INTRA_COLUMNS = ['Symbol', 'Time', 'Open','High', 'Low', 'Close', \
                 'Volume','Trades','WgtdPrc','VWAP','Imbalance','Bid','Ask',\
                 'BidSz','AskSz']

RATES_COLUMNS = ['Date', 'Treasury_1m', 'Treasury_2m', 'Treasury_3m',
                 'Treasury_4m', 'Treasury_6m', 'Treasury_1y', 'Treasury_2y',
                 'Treasury_3y', 'Treasury_5y', 'Treasury_7y', 'Treasury_10y',
                 'Treasury_20y', 'Treasury_30y', 'Realrate_5y', 'Realrate_7y',
                 'Realrate_10y', 'Realrate_20y', 'Realrate_30y']


def login(username: str, key: str):
    """
    Logs in to the API to provide data that is not publically available.
    Throws an error if the username/key is wrong, or if there's a connection error.

    Args:
        username (str): The email that you signed up with
        key (str): The key that you got at www.moabdb.com/account/member-api

    Returns:
        None: On success, this will return nothing

    Raises:
        errors.MoabResponseError: If there's a problem interpreting the response
        errors.MoabRequestError: If the server has a problem interpreting the request,
            or if an invalid parameter is passed
        errors.MoabInternalError: If the server runs into an unrecoverable error internally
        errors.MoabHttpError: If there's a problem transporting the payload or receiving a response
        errors.MoabUnauthorizedError: If the user is not authorized to request the datatype
        errors.MoabNotFoundError: If the data requested wasn't found
        errors.MoabUnknownError: If the error code couldn't be parsed

    Example::

        import moabdb as mdb
        mdb.login("your-signup-email@mail.com", "secret_key")
        print("Login succeeded")

    """

    # Create a login request
    req = proto_wrapper.REQUEST()
    req.token = key
    req.username = username

    res = req.send(DB_URL + 'login/v1/')

    res.throw()
    # pylint: disable=global-statement
    global API_KEY
    global API_USERNAME

    API_KEY = key
    API_USERNAME = username
