
import re

from os.path import dirname, join

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from ouimeaux.environment import Environment

__author__ = 'martymulligan'

# Logger: used for debug lines, like "LOGGER.debug(xyz)". These
# statements will show up in the command line when running Mycroft.
LOGGER = getLogger(__name__)

# The logic of each skill is contained within its own class, which inherits
# base methods from the MycroftSkill class with the syntax you can see below:
# "class ____Skill(MycroftSkill)"
class WemoSkill(MycroftSkill):

    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(WemoSkill, self).__init__(name="WemoSkill")

    def on_switch(self, switch):
        LOGGER.debug("Switch detected: %s" % switch.name)
        self.speak('Discovered a switch named ' + switch.name)

    def on_motion(self, motion):
        LOGGER.debug("Motion detected on ", motion.name)

    # This method loads the files needed for the skill's functioning, and
    # creates and registers each intent that the skill uses
    def initialize(self):
        LOGGER.debug("Initializing WeMo Environment");

        self.env = Environment(self.on_switch, self.on_motion)
        self.env.start()
        self.env.discover(seconds=5)

        self.load_data_files(dirname(__file__))
        prefixes = [
            'toggle', 'tockle', 'taco']
        self.__register_prefixed_regex(prefixes, "(?P<ToggleWords>.*)")

        listprefixes = [
            'list wemo', 'identify wemo', 'get wemo']
        self.__register_prefixed_regex(listprefixes, "(?P<ListWords>.*)")

        # switch intent
        intent = IntentBuilder("WemoSwitchIntent").require(
            "WemoSwitchKeyword").require("ToggleWords").build()
        self.register_intent(intent, self.handle_wemo_switch_intent)

        # discover intent
        intent = IntentBuilder("WemoDiscoverIntent").require(
            "WemoDiscoverKeyword").build()
        self.register_intent(intent, self.handle_wemo_discover_intent)

        # list switches intent
        intent = IntentBuilder("WemoListIntent").require(
            "WemoListKeyword").require("ListWords").build()
        self.register_intent(intent, self.handle_wemo_list_intent)


    def __register_prefixed_regex(self, prefixes, suffix_regex):
        for prefix in prefixes:
            self.register_regex(prefix + ' ' + suffix_regex)


    def handle_wemo_switch_intent(self, message):
        togglewords = message.data.get("ToggleWords")
        try:
            device = self.env.get_switch(togglewords)
            device.toggle()

        except:
            LOGGER.debug("Unknown WeMo device: ", togglewords)
            self.speak("I don't know a device called ", togglewords)

    def handle_wemo_list_intent(self, message):
        # listwords are the type of thing you want to list
        # like "mycroft list switches"
        listwords = message.data.get("ListWords")
        LOGGER.debug("Wemo list")
        LOGGER.debug(listwords)

        try:
            self.env.start()
            switches = self.env.list_switches()
            LOGGER.debug("Wemo switches:")
            LOGGER.debug(switches)
            num_switches = len(switches)

            if num_switches > 0:
                self.speak("I found " + str(num_switches) + " wemo switches.")
            else:
                self.speak("I didn't find any wemo switches")

            for switch in switches:
                self.speak(switch)

        except Exception as e:
            LOGGER.debug("Error occurred listing Wemo switches: "+e.message)
            LOGGER.debug(e)
            self.speak("uh. ah.")



    def handle_wemo_discover_intent(self, message):
        try:
            self.env = Environment(self.on_switch, self.on_motion)
            self.env.start()
            self.env.discover(seconds=5)

        except:
            LOGGER.debug("Error occurred discovering Wemo devices")
            self.speak("ahr. ah.")

    # The "stop" method defines what Mycroft does when told to stop during
    # the skill's execution. In this case, since the skill's functionality
    # is extremely simple, the method just contains the keyword "pass", which
    # does nothing.
    def stop(self):
        pass

# The "create_skill()" method is used to create an instance of the skill.
# Note that it's outside the class itself.
def create_skill():
    return WemoSkill()
