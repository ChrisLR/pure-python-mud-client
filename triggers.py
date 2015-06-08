#this is a basic class structure for triggers lifted from class materials.
#change so it runs of regex.
#trigger dictionary - key is regex, value is action. 
#thus triggers can be nested.
#but how do we keep track of active triggers? and what if there are a lot?
#how many is too many threads?
#maybe each trigger should be a stand alone thread? can all threads snoop
#the same queue?

import re


triggerDict = {}

# triggerDict['regex':action,}

triggerDict['^What name shall you be known by, adventurer\?$':"Darklight",}

class Trigger(object):
    def evaluate(self, line):
        pass

class RegexTrigger(Trigger):
    def __init__(self, pattern):
        self.trigger = re.compile(pattern)
        
    def detectPattern(self, text):
        result = re.findall(self.trigger, text)
        if result:
                return True
        return False
                
class RunTrigger(RegexTrigger):
    def evaluate(self, line):
        return self.detectPattern(line)

        
class NotTrigger(Trigger):
    def __init__(self, trigger):
        self.trigger = trigger
        
    def evaluate(self, story):
        return not self.trigger.evaluate(story)

class AndTrigger(Trigger):
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2
        
    def evaluate(self, story):
        return self.trigger1.evaluate(story) and self.trigger2.evaluate(story)

class OrTrigger(Trigger):
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2
        
    def evaluate(self, story):
        return self.trigger1.evaluate(story) or self.trigger2.evaluate(story)

