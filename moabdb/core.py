#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# moabdb - Online finance database
# https://github.com/MoabDB
# https://moabdb.com
# Copyright 2022-2023
#


"""

All data retrieved using the ``moabdb`` API are returned as pandas DataFrames.

Usage without login
-------------------

>>> import moabdb as mdb
>>> df = mdb.get_equity("AAPL", "6m") # Get 6 months of AAPL daily data


Usage with login
----------------

>>> import moabdb as mdb
>>> mdb.login("your_email@example.com", "moabdb_api_key")
>>> df = mdb.get_equity("AAPL", "6m", intraday=True) # Get 6 months of AAPL intraday data

For information on subscriptions visit https://moabdb.com.

To view the source code visit https://github.com/MoabDB.

"""

from . import constants
from . import errors
from . import timewindows
from .lib import _check_access, _server_req
from .constants import pd, Union, cf


def get_equity(tickers: Union[str, list],
               sample: str = "1m",
               start: str = None,
               end: str = None,
               intraday: bool = False) -> pd.DataFrame:
    """

    Returns a ``pandas.DataFrame`` of historical price and volume information
    for the ticker(s) requested.

    Modifying the intraday flag changes the return dataframe between
    daily-level and intraday-level data. Daily-level data is returned by
    default, and intraday-level data is returned when the intraday flag is set
    to ``True``. Intraday data is only available to users with an active
    subscription to intraday data from moabdb.com. Daily level data
    reports aggregated information for trades between 9:30 AM and 4:00 PM
    Eastern. Intraday level data reports aggregated information by second
    for trades between 8:00 AM and 6:00 PM Eastern.


    Parameters
    ----------
    tickers : str or list of str
        The ticker(s) to look up. Accepts a single ticker as a string or
        multiple tickers as a list of strings.

        If a single ticker (str) is provided, the resulting DataFrame
        will have a Datetime index, and the columns will represent individual
        data variables, such as "Open", "High", "Low", "Close", etc.

        If multiple tickers (List[str]) are provided, the resulting DataFrame
        will have a Datetime index, and the columns will have a multi-index
        with the first level being the ticker symbol, and the second level
        being the data variable, such as "Open", "High", "Low", "Close", etc.
        For example, if you pass ["AAPL", "MSFT"], the DataFrame columns will look like:

        +-----------+-----------+-----------+-----------+-----------+
        |           |   'AAPL'  |   'MSFT'  |   'AAPL'  |   'MSFT'  |
        +===========+===========+===========+===========+===========+
        |           |   Open    |   Open    |   High    |   High    |
        +-----------+-----------+-----------+-----------+-----------+
        | Datetime  |           |           |           |           |
        +-----------+-----------+-----------+-----------+-----------+

    sample : str, optional
        Sample period length. It can be used alone or with ``start`` | ``end``.

    start : str, optional
        Sample start date. Requires one of ``end`` or ``sample``.

    end : str, optional
        Sample end date. Requires one of ``start`` or ``sample``.

    intraday : bool, optional, default False
        Set to True to return intraday data.
        Default is False to return end-of-day data.
        See moabdb.com for subscriptions for intraday access.


    Returns
    -------
    out : pandas.DataFrame
        DataFrame containing equity price and volume information, indexed by datetime64.
        The format of the DataFrame depends on the request type.

        If the request is for a single ticker, the DataFrame will be returned with single
        index.If the request is for multiple tickers, the DataFrame will be returned
        with multi-index columns, with the first level being the ticker symbol.


        Daily data includes the following variables:

        +-----------------------+--------------------------------------------+
        | DataFrame Column      | Variable Description                       |
        +=======================+============================================+
        | ``Symbol`` (str)      | Ticker symbol of the equity.               |
        +-----------------------+--------------------------------------------+
        | ``Open`` (float)      | Opening trade price.                       |
        +-----------------------+--------------------------------------------+
        | ``High`` (float)      | Highest trade price.                       |
        +-----------------------+--------------------------------------------+
        | ``Low`` (float)       | Lowest trade price.                        |
        +-----------------------+--------------------------------------------+
        | ``Close`` (float)     | Closing trade price.                       |
        +-----------------------+--------------------------------------------+
        | ``VWAP`` (float)      | Volume-weighted average price.             |
        +-----------------------+--------------------------------------------+
        | ``BidPrc`` (float)    | Bid price.                                 |
        +-----------------------+--------------------------------------------+
        | ``AskPrc`` (float)    | Ask price.                                 |
        +-----------------------+--------------------------------------------+
        | ``Volume`` (int)      | Volume traded.                             |
        +-----------------------+--------------------------------------------+
        | ``Trades`` (int)      | Number of trades.                          |
        +-----------------------+--------------------------------------------+


        Intraday data includes the following variables:

        +-----------------------+--------------------------------------------------+
        | DataFrame Column      | Variable Description                             |
        +=======================+==================================================+
        | ``Symbol`` (str)      | Ticker symbol of the equity.                     |
        +-----------------------+--------------------------------------------------+
        | ``Trades`` (int)      | Number of trades.                                |
        +-----------------------+--------------------------------------------------+
        | ``Volume`` (int)      | Volume traded.                                   |
        +-----------------------+--------------------------------------------------+
        | ``Imbalance`` (int)   | Buy-initiated volume minus sell-initiated volume.|
        +-----------------------+--------------------------------------------------+
        | ``Close`` (float)     | Closing trade price.                             |
        +-----------------------+--------------------------------------------------+
        | ``VWAP`` (float)      | Volume-weighted average price.                   |
        +-----------------------+--------------------------------------------------+
        | ``BidPrc`` (float)    | Bid price.                                       |
        +-----------------------+--------------------------------------------------+
        | ``AskPrc`` (float)    | Ask price.                                       |
        +-----------------------+--------------------------------------------------+
        | ``BidSz`` (int)       | Round lots available at BidPrc.                  |
        +-----------------------+--------------------------------------------------+
        | ``AskSz`` (int)       | Round lots available at AskPrc.                  |
        +-----------------------+--------------------------------------------------+

    .. note::

        - If the request is for a single ticker, the DataFrame will be returned
          with individual columns representing variables.

        - If the request is for multiple tickers, the DataFrame will have multi-index
          columns with the first level being the ticker symbol, and the second level
          being the data variable.


    Raises
    ------
    errors.MoabResponseError:
        If there's a problem interpreting the response
    errors.MoabRequestError:
        If the server has a problem interpreting the request,
        or if an invalid parameter is passed
    errors.MoabInternalError:
        If the server runs into an unrecoverable error internally
    errors.MoabHttpError:
        If there's a problem transporting the payload or receiving a response
    errors.MoabUnauthorizedError:
        If the user is not authorized to request the datatype
    errors.MoabNotFoundError:
        If the data requested wasn't found
    errors.MoabUnknownError:
        If the error code couldn't be parsed

    """

    # Check intraday authorization
    if intraday is True:
        equity_freq = "intraday_stocks"
        columns = constants.INTRA_COLUMNS
        if not _check_access():
            raise errors.MoabRequestError(
                "Intraday needs API credentials, see moabdb.com")
    else:
        equity_freq = "daily_stocks"
        columns = constants.DAILY_COLUMNS

    # String time to integer time
    start_tm, end_tm = timewindows.get_unix_dates(sample, start, end)

    # Single ticker request
    if isinstance(tickers, str):
        return_db = _server_req(
            str.upper(tickers), start_tm, end_tm, equity_freq)
        return_db = return_db[columns]
        return_db = return_db.set_index(columns[1])

    # Multiple tickers request
    elif isinstance(tickers, list):
        processed = []
        calls = len(tickers)
        with cf.ThreadPoolExecutor() as pool:
            for result in pool.map(_server_req, tickers, [start_tm]*calls,
                                   [end_tm]*calls, [equity_freq]*calls):
                processed.append(result)
        return_db = pd.concat(processed)[columns]
        return_db = return_db.set_index(columns[0:2]).unstack(0)

    # Unknown ticker request
    else:
        raise errors.MoabRequestError("Invalid window type")

    # Round float columns
    float_columns = return_db.select_dtypes(include=['float32', 'float64'])
    if float_columns.size > 0:
        return_db[float_columns.columns] = float_columns.astype(
            'float64').round(4)

    return return_db


def get_rates(sample: str = "1y",
              start: str = None,
              end: str = None) -> pd.DataFrame:
    """

    Returns a ``pandas.DataFrame`` of historical interest rates.

    Modifying the ``sample``, ``start``, and ``end`` parameters allows for the
    customization of the date range for the returned data. If the ``sample``
    parameter is specified, the most recent data for that sample length
    is returned. If the ``start`` and ``end`` parameters are specified, the
    data for that specific date range is returned.


    Parameters
    ----------
    sample : str, optional
        Sample period length. It can be used alone or with ``start`` | ``end``.

    start : str, optional
        Sample start date. Requires one of ``end`` or ``sample``.

    end : str, optional
        Sample end date. Requires one of ``start`` or ``sample``.


    Returns
    -------
    out : pandas.DataFrame
        DataFrame containing treasury data, indexed by datetime64. Each column
        represents a different term for the treasury yield.

        Data includes the following variables:

        +-------------------+--------------------------------------------+
        | DataFrame Column  | Variable Description                       |
        +===================+============================================+
        | ``Treasury_1m``   | Treasury yield for a 1-month maturity.     |
        +-------------------+--------------------------------------------+
        | ``Treasury_2m``   | Treasury yield for a 2-month maturity.     |
        +-------------------+--------------------------------------------+
        | ``Treasury_3m``   | Treasury yield for a 3-month maturity.     |
        +-------------------+--------------------------------------------+
        | ``Treasury_4m``   | Treasury yield for a 4-month maturity.     |
        +-------------------+--------------------------------------------+
        | ``Treasury_6m``   | Treasury yield for a 6-month maturity.     |
        +-------------------+--------------------------------------------+
        | ``Treasury_1y``   | Treasury yield for a 1-year maturity.      |
        +-------------------+--------------------------------------------+
        | ``Treasury_2y``   | Treasury yield for a 2-year maturity.      |
        +-------------------+--------------------------------------------+
        | ``Treasury_3y``   | Treasury yield for a 3-year maturity.      |
        +-------------------+--------------------------------------------+
        | ``Treasury_5y``   | Treasury yield for a 5-year maturity.      |
        +-------------------+--------------------------------------------+
        | ``Treasury_7y``   | Treasury yield for a 7-year maturity.      |
        +-------------------+--------------------------------------------+
        | ``Treasury_10y``  | Treasury yield for a 10-year maturity.     |
        +-------------------+--------------------------------------------+
        | ``Treasury_20y``  | Treasury yield for a 20-year maturity.     |
        +-------------------+--------------------------------------------+
        | ``Treasury_30y``  | Treasury yield for a 30-year maturity.     |
        +-------------------+--------------------------------------------+
        | ``Realrate_5y``   | Real interest rate for a 5-year maturity.  |
        +-------------------+--------------------------------------------+
        | ``Realrate_7y``   | Real interest rate for a 7-year maturity.  |
        +-------------------+--------------------------------------------+
        | ``Realrate_10y``  | Real interest rate for a 10-year maturity. |
        +-------------------+--------------------------------------------+
        | ``Realrate_20y``  | Real interest rate for a 20-year maturity. |
        +-------------------+--------------------------------------------+
        | ``Realrate_30y``  | Real interest rate for a 30-year maturity. |
        +-------------------+--------------------------------------------+

    Raises
    ------
    errors.MoabResponseError:
        If there's a problem interpreting the response
    errors.MoabRequestError:
        If the server has a problem interpreting the request,
        or if an invalid parameter is passed
    errors.MoabInternalError:
        If the server runs into an unrecoverable error internally
    errors.MoabHttpError:
        If there's a problem transporting the payload or receiving a response
    errors.MoabUnauthorizedError:
        If the user is not authorized to request the datatype
    errors.MoabNotFoundError:
        If the data requested wasn't found
    errors.MoabUnknownError:
        If the error code couldn't be parsed

    """

    # Check authorization
    if not _check_access():
        raise errors.MoabRequestError(
            "Premium datasets need API credentials, see moabdb.com")

    # String time to integer time
    start_tm, end_tm = timewindows.get_unix_dates(sample, start, end)

    # Request treasury data
    columns = constants.RATES_COLUMNS
    return_db = _server_req("INTERNAL_TREASURY",
                            start_tm, end_tm, "treasuries")

    # Format treasury data
    return_db = return_db[columns].set_index(columns[0])

    return return_db
