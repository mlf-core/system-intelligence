

def bytes_to_hreadable_string(nbytes: int) -> str:
    """
    Transforms bytes into a human readable string with attached appropriate unit

    :param nbytes: number of bytes
    :return: human readable formatted string of bytes with unit
    """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    # No result
    if not nbytes or nbytes == 'NA':
        return ''

    if isinstance(nbytes, str):
        nbytes = int(nbytes)
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')

    return f'{f} {suffixes[i]}'


def hz_to_hreadable_string(hz: int) -> str:
    """
    Transforms hertz into a human readable string with attached appropriate unit

    :param: number of hertz
    :return: human readable formatted string of hertz with unit
    """
    suffixes = ['Hz', 'kHz', 'MHz', 'GHz']

    # No result
    if not hz or hz == 'NA':
        return ''

    if isinstance(hz, str):
        hz = int(hz)
    i = 0
    while hz >= 1000 and i < len(suffixes) - 1:
        hz /= 1000.
        i += 1
    f = ('%.2f' % hz).rstrip('0').rstrip('.')

    return f'{f} {suffixes[i]}'
