from enum import Enum

import arc


class JobStatuses(Enum):
    """
    Possible values for job status
    """
    COMPLETED = "completed"
    IN_PROGRESS = "in progress"
    NOT_STARTED = "not started"
    NOT_SUBMITTED = "not submitted"
    FAILED = "failed"


#: Map job statuses as given by ARC to statuses in our simplified model
ARC_STATUS_MAPPING = {
    "Undefined": JobStatuses.FAILED,
    "Accepted": JobStatuses.NOT_SUBMITTED,
    "Preparing": JobStatuses.NOT_SUBMITTED,
    "Submitting": JobStatuses.NOT_SUBMITTED,
    "Hold": JobStatuses.IN_PROGRESS,
    "Queuing": JobStatuses.NOT_STARTED,
    "Running": JobStatuses.IN_PROGRESS,
    "Finishing": JobStatuses.IN_PROGRESS,
    "Finished": JobStatuses.COMPLETED,
    "Killed": JobStatuses.FAILED,
    "Failed": JobStatuses.FAILED,
    "Deleted": JobStatuses.FAILED,
    "Other": JobStatuses.FAILED
}


class LogLevels(Enum):
    """
    Log levels for specifying the level of details to include in the logs. These levels and
    descriptions come straight from the ARC library
    """

    #: DEBUG level designates finer-grained informational events which should only be used for
    #: debugging purposes
    DEBUG = arc.DEBUG

    #: VERBOSE level designates fine-grained informational events that will give additional
    #: information about the application
    VERBOSE = arc.VERBOSE

    #: INFO level designates informational messages that highlight the progress of the
    #: application at coarse-grained level
    INFO = arc.INFO

    #: WARNING level designates potentially harmful situations
    WARNING = arc.WARNING

    #: ERROR level designates error events that might still allow the application to continue
    #: running
    ERROR = arc.ERROR

    #: FATAL level designates very severe error events that will presumably lead the application to
    #: abort
    FATAL = arc.FATAL
