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
    """Create a memory-map to an array stored in a *binary* file on disk.

    Memory-mapped files are used for accessing small segments of large files
    on disk, without reading the entire file into memory.  NumPy's
    memmap's are array-like objects.  This differs from Python's ``mmap``
    module, which uses file-like objects.

    This subclass of ndarray has some unpleasant interactions with
    some operations, because it doesn't quite fit properly as a subclass.
    An alternative to using this subclass is to create the ``mmap``
    object yourself, then create an ndarray with ndarray.__new__ directly,
    passing the object created in its 'buffer=' parameter.

    This class may at some point be turned into a factory function
    which returns a view into an mmap buffer.

    Flush the memmap instance to write the changes to the file. Currently there
    is no API to close the underlying ``mmap``. It is tricky to ensure the
    resource is actually closed, since it may be shared between different
    memmap instances.


    Parameters
    ----------
    filename : str, file-like object, or pathlib.Path instance
        The file name or file object to be used as the array data buffer.
    dtype : data-type, optional
        The data-type used to interpret the file contents.
        Default is `uint8`.
    mode : {'r+', 'r', 'w+', 'c'}, optional
        The file is opened in this mode:

        +------+-------------------------------------------------------------+
        | 'r'  | Open existing file for reading only.                        |
        +------+-------------------------------------------------------------+
        | 'r+' | Open existing file for reading and writing.                 |
        +------+-------------------------------------------------------------+
        | 'w+' | Create or overwrite existing file for reading and writing.  |
        |      | If ``mode == 'w+'`` then `shape` must also be specified.    |
        +------+-------------------------------------------------------------+
        | 'c'  | Copy-on-write: assignments affect data in memory, but       |
        |      | changes are not saved to disk.  The file on disk is         |
        |      | read-only.                                                  |
        +------+-------------------------------------------------------------+

        Default is 'r+'.
    offset : int, optional
        In the file, array data starts at this offset. Since `offset` is
        measured in bytes, it should normally be a multiple of the byte-size
        of `dtype`. When ``mode != 'r'``, even positive offsets beyond end of
        file are valid; The file will be extended to accommodate the
        additional data. By default, ``memmap`` will start at the beginning of
        the file, even if ``filename`` is a file pointer ``fp`` and
        ``fp.tell() != 0``.
    shape : tuple, optional
        The desired shape of the array. If ``mode == 'r'`` and the number
        of remaining bytes after `offset` is not a multiple of the byte-size
        of `dtype`, you must specify `shape`. By default, the returned array
        will be 1-D with the number of elements determined by file size
        and data-type.
    order : {'C', 'F'}, optional
        Specify the order of the ndarray memory layout:
        :term:`row-major`, C-style or :term:`column-major`,
        Fortran-style.  This only has an effect if the shape is
        greater than 1-D.  The default order is 'C'.

    Attributes
    ----------
    filename : str or pathlib.Path instance
        Path to the mapped file.
    offset : int
        Offset position in the file.
    mode : str
        File mode.

    Methods
    -------
    flush
        Flush any changes in memory to file on disk.
        When you delete a memmap object, flush is called first to write
        changes to disk.


    See also
    --------
    lib.format.open_memmap : Create or load a memory-mapped ``.npy`` file.

    Notes
    -----
    The memmap object can be used anywhere an ndarray is accepted.
    Given a memmap ``fp``, ``isinstance(fp, numpy.ndarray)`` returns
    ``True``.

    Memory-mapped files cannot be larger than 2GB on 32-bit systems.

    When a memmap causes a file to be created or extended beyond its
    current size in the filesystem, the contents of the new part are
    unspecified. On systems with POSIX filesystem semantics, the extended
    part will be filled with zero bytes.

    Examples
    --------
    >>> data = np.arange(12, dtype='float32')
    >>> data.resize((3,4))

    This example uses a temporary file so that doctest doesn't write
    files to your directory. You would use a 'normal' filename.

    >>> from tempfile import mkdtemp
    >>> import os.path as path
    >>> filename = path.join(mkdtemp(), 'newfile.dat')

    Create a memmap with dtype and shape that matches our data:

    >>> fp = np.memmap(filename, dtype='float32', mode='w+', shape=(3,4))
    >>> fp
    memmap([[0., 0., 0., 0.],
            [0., 0., 0., 0.],
            [0., 0., 0., 0.]], dtype=float32)

    Write data to memmap array:

    >>> fp[:] = data[:]
    >>> fp
    memmap([[  0.,   1.,   2.,   3.],
            [  4.,   5.,   6.,   7.],
            [  8.,   9.,  10.,  11.]], dtype=float32)

    >>> fp.filename == path.abspath(filename)
    True

    Flushes memory changes to disk in order to read them back

    >>> fp.flush()

    Load the memmap and verify data was stored:

    >>> newfp = np.memmap(filename, dtype='float32', mode='r', shape=(3,4))
    >>> newfp
    memmap([[  0.,   1.,   2.,   3.],
            [  4.,   5.,   6.,   7.],
            [  8.,   9.,  10.,  11.]], dtype=float32)

    Read-only memmap:

    >>> fpr = np.memmap(filename, dtype='float32', mode='r', shape=(3,4))
    >>> fpr.flags.writeable
    False

    Copy-on-write memmap:

    >>> fpc = np.memmap(filename, dtype='float32', mode='c', shape=(3,4))
    >>> fpc.flags.writeable
    True

    It's possible to assign to copy-on-write array, but values are only
    written into the memory copy of the array, and not written to disk:

    >>> fpc
    memmap([[  0.,   1.,   2.,   3.],
            [  4.,   5.,   6.,   7.],
            [  8.,   9.,  10.,  11.]], dtype=float32)
    >>> fpc[0,:] = 0
    >>> fpc
    memmap([[  0.,   0.,   0.,   0.],
            [  4.,   5.,   6.,   7.],
            [  8.,   9.,  10.,  11.]], dtype=float32)

    File on disk is unchanged:

    >>> fpr
    memmap([[  0.,   1.,   2.,   3.],
            [  4.,   5.,   6.,   7.],
            [  8.,   9.,  10.,  11.]], dtype=float32)

    Offset into a memmap:

    >>> fpo = np.memmap(filename, dtype='float32', mode='r', offset=16)
    >>> fpo
    memmap([  4.,   5.,   6.,   7.,   8.,   9.,  10.,  11.], dtype=float32)

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
    Gets treasury data from the MoabDB API.

    Args:
        sample (str, optional): Sample length, required if "start" or "end" is missing.
        start (str, optional): Beginning date of sample, required if "end" or "sample" is missing.
        end (str, optional): Ending date of sample, required if "start" or "sample" is missing.

    Raises:
        errors.MoabResponseError: If there's a problem interpreting the response.
        errors.MoabRequestError: If the server has a problem interpreting the request,
            or if an invalid parameter is passed.
        errors.MoabInternalError: If the server runs into an unrecoverable error internally.
        errors.MoabHttpError: If there's a problem transporting the payload or receiving a response.
        errors.MoabUnauthorizedError: If the user is not authorized to request the datatype.
        errors.MoabNotFoundError: If the data requested wasn't found.
        errors.MoabUnknownError: If the error code couldn't be parsed.

    Returns:
        pandas.DataFrame: A DataFrame containing daily treasury data.
            Index: Date (datetime64): Date of the data point as YYYY-MM-DD.
            Columns:
                - Treasury_1m (float): Treasury yield for a 1-month maturity.
                - Treasury_2m (float): Treasury yield for a 2-month maturity.
                - Treasury_3m (float): Treasury yield for a 3-month maturity.
                - Treasury_4m (float): Treasury yield for a 4-month maturity.
                - Treasury_6m (float): Treasury yield for a 6-month maturity.
                - Treasury_1y (float): Treasury yield for a 1-year maturity.
                - Treasury_2y (float): Treasury yield for a 2-year maturity.
                - Treasury_3y (float): Treasury yield for a 3-year maturity.
                - Treasury_5y (float): Treasury yield for a 5-year maturity.
                - Treasury_7y (float): Treasury yield for a 7-year maturity.
                - Treasury_10y (float): Treasury yield for a 10-year maturity.
                - Treasury_20y (float): Treasury yield for a 20-year maturity.
                - Treasury_30y (float): Treasury yield for a 30-year maturity.
                - Realrate_5y (float): Real interest rate for a 5-year maturity.
                - Realrate_7y (float): Real interest rate for a 7-year maturity.
                - Realrate_10y (float): Real interest rate for a 10-year maturity.
                - Realrate_20y (float): Real interest rate for a 20-year maturity.
                - Realrate_30y (float): Real interest rate for a 30-year maturity.

    Examples:

        - Request the last year of treasury data:
            import moabdb as mdb
            df = mdb.get_rates("1y")

        - Request a specific month of data:
            import moabdb as mdb
            df = mdb.get_rates(start="2022-04-01", sample="1m")

        - Request treasury data for a specific date range:
            import moabdb as mdb
            df = mdb.get_rates(start="2020-01-01", end="2020-12-31")

    """

    # Check authorization
    if not _check_access():
        raise errors.MoabRequestError(
            "Premium datasets needs API credentials, see moabdb.com")

    # String time to integer time
    start_tm, end_tm = timewindows.get_unix_dates(sample, start, end)

    # Request treasury data
    columns = constants.RATES_COLUMNS
    return_db = _server_req("INTERNAL_TREASURY",
                            start_tm, end_tm, "treasuries")

    # Format treasury data
    return_db = return_db[columns].set_index(columns[0])

    return return_db
