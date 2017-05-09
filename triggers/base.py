import abc


class BaseTrigger(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, input_trigger):
        self.enabled = False
        self.input_trigger = input_trigger

    @abc.abstractmethod
    def evaluate(self, message):
        pass

    @abc.abstractmethod
    def trigger(self, message):
        pass


class SimpleTrigger(BaseTrigger):
    def __init__(self, input_trigger, output_command):
        super().__init__(input_trigger)
        self.output_command = output_command

    def evaluate(self, message):
        if self.input_trigger in message:
            return True

    def trigger(self, message):
        return self.output_command
