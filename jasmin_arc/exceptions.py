class InvalidConfigError(Exception):
    """
    Exception thrown when config file is invalid
    """


class ProxyGenerationError(Exception):
    """
    Proxy could not be created from key and certificate
    """


class InvalidJobDescription(Exception):
    """
    Job description XML is invalid
    """


class JobSubmissionError(Exception):
    """
    Job could not be submitted to any targets
    """


class NoTargetsAvailableError(Exception):
    """
    No execution targets could be found to submit jobs to
    """


class JobNotFoundError(Exception):
    """
    A job with the given ID could not be found
    """


class InputFileError(Exception):
    """
    Input file does not exist or is not a file
    """
