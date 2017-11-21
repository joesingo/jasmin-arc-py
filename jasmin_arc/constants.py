from enum import Enum

import arc


class JobStatuses(Enum):
    """
    Possible values for job status
    """
    COMPLETED = 'completed'
    IN_PROGRESS = 'in progress'
    NOT_STARTED = 'not started'
    NOT_SUBMITTED = 'not submitted'
    FAILED = 'failed'


class LogLevels(Enum):
    """
    Log levels for specifying the level of details to include in the logs. These levels and
    descriptions come straight from the ARC library
    """

    DEBUG = arc.DEBUG
    """
    DEBUG level designates finer-grained informational events which should only be used for
    debugging purposes
    """

    VERBOSE = arc.VERBOSE
    """
    VERBOSE level designates fine-grained informational events that will give additional information
    about the application
    """

    INFO = arc.INFO
    """
    INFO level designates informational messages that highlight the progress of the application at
    coarse-grained level
    """

    WARNING = arc.WARNING
    """
    WARNING level designates potentially harmful situations
    """

    ERROR = arc.ERROR
    """
    ERROR level designates error events that might still allow the application to continue running
    """

    FATAL = arc.FATAL
    """
    FATAL level designates very severe error events that will presumably lead the application to
    abort
    """


