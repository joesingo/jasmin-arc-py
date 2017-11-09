class DictByAttr(dict):
    """
    Override dict to access items using `.`
    """
    def __getattr__(self, key):
        return self.__getitem__(key)


# Constants to represent the possible statuses for a job
JOB_STATUSES = DictByAttr((
    ("COMPLETED", 'completed'),
    ("IN_PROGRESS", 'in progress'),
    ("NOT_STARTED", 'not started'),
    ("NOT_SUBMITTED", 'not submitted'),
    ("FAILED", 'failed')
))

