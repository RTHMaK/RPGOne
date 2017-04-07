import logging
import os

PYTHONHASHSEED = '2157'

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

class ConfigurationError(Exception):
    def __init__(self, message):
        super(ConfigurationError, self).__init__()
        self.message = message

    def __str__(self):
        return repr(self.message)


def ensure_pythonhashseed_set():
    message = """You must set PYTHONHASHSEED so that we get repeatable results.
    You can do this with the command `export PYTHONHASHSEED=%s`.
    See https://docs.python.org/3/using/cmdline.html#envvar-PYTHONHASHSEED for more info.
    """
    assert os.environ.get('PYTHONHASHSEED', None) == PYTHONHASHSEED, message % PYTHONHASHSEED


def log_keras_version_info():
    import keras
    logger.info("Keras version: " + keras.__version__)
    from keras import backend as K
    try:
        backend = K.backend()
    except AttributeError:
        backend = K._BACKEND  # pylint: disable=protected-access
    if backend == 'theano':
        import theano
        logger.info("Theano version: " + theano.__version__)
    elif backend == 'tensorflow':
        import tensorflow
        logger.info("Tensorflow version: " + tensorflow.__version__)  # pylint: disable=no-member
