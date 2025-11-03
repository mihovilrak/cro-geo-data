import logging
import sys
import types

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger.addHandler(handler)

def exception_handler(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: types.TracebackType,
) -> None:
    """
    Handle uncaught exceptions.

    Args:
        exc_type (type[BaseException]): The type of the exception.
        exc_value (BaseException): The value of the exception.
        exc_traceback (types.TracebackType): The traceback of the exception.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        return

    logger.error(
        f"Uncaught exception: {exc_type.__name__}: {exc_value}",
        exc_info=(exc_type, exc_value, exc_traceback),
    )
    sys.exit(1)

sys.excepthook = exception_handler
