import logging
import inspect
import os

log = logging.getLogger(__name__)

def log_variables(**kwargs):
    frame = inspect.currentframe().f_back
    filename = frame.f_globals['__file__']
    relative_path = os.path.relpath(filename)
    message = f'\nFile: {relative_path}, \n ' + ', \n '.join(f'{k}: {v}' for k, v in kwargs.items())
    log.info(message)