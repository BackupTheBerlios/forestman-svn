import gettext
gettext.install('ForestMan')

TAX_RATE=21
TAX_MULTIPLIER = 1+ (TAX_RATE/100)

def join(*args):
    ret = {}
    for a in args:
        ret.update(a)
    return ret


class MiddleLayerError(StandardError):
    """Base class for all errors that occur in the middle layer
    Attibutes:
        errortext = internationalised text describing the error
    """
    def __init__(self, errortext):
        self.errortext = errortext
    def __str__(self):
        return self.errortext
    