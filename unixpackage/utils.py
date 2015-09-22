from subprocess import call, Popen, PIPE
from unixpackage import exceptions
import requests
import json
import io


def return_code_zero(command):
    """Returns True if command called has return code zero."""
    return call(command, stdout=PIPE, stderr=PIPE) == 0

def check_output(command, stdout=PIPE, stderr=PIPE):
    """Re-implemented subprocess.check_output since it is not available < python 2.7."""
    return Popen(command, stdout=stdout, stderr=stderr).communicate()[0]

def check_call(command, shell=True):
    """Re-implemented subprocess.check_call since it is not available < python 2.7."""
    process = Popen(command, shell=shell)
    process.communicate()
    if process.returncode != 0:
        raise exceptions.CalledProcessError
    return

def is_string(obj):
    """Is the object a string/unicode?"""
    return str(type(obj)) == "<type 'unicode'>" or str(type(obj)) == "<class 'str'>"

def get_json_from_file(cache_filename):
    with open(cache_filename, 'r') as cache_read_handle:
        return json.loads(cache_read_handle.read())

def save_json_to_file(cache_filename, contents):
    with open(cache_filename, 'w') as cache_write_handle:
        cache_write_handle.write(json.dumps(contents))

def get_request(url):
    try:
        req = requests.get(url)
    except requests.exceptions.ConnectionError:
        raise exceptions.ConnectionFailure((
            "Failure when connecting to {0} "
            "Is your internet working?"
        ).format(url))
    return req

def _write(handle, message):
    if isinstance(handle, io.TextIOWrapper):
        handle.write(message)
    else:
        handle.write(message.encode('utf8'))
    handle.flush()

def log(message):
    """Output to stdout."""
    import sys
    _write(sys.stdout, message)

def warn(message):
    """Output to stderr."""
    import sys
    _write(sys.stderr, message)
