import abc


class BaseAlias(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, output_trigger):
        self.enabled = False
        self.output_trigger = output_trigger

    @abc.abstractmethod
    def evaluate(self, message):
        pass

    @abc.abstractmethod
    def trigger(self, message):
        pass


class SimpleAlias(BaseAlias):
    def __init__(self, output_trigger, output_command):
        super().__init__(output_trigger)
        self.output_command = output_command

    def evaluate(self, message):
        if self.output_trigger in message:
            return True

    def trigger(self, message):
        return self.output_command
