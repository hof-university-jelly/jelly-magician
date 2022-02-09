from pydobot import Dobot
from pydobot.message import Message
from pydobot.enums.CommunicationProtocolIDs import CommunicationProtocolIDs

"""
Adds functionality to the pydobot Dobot class from the python sdk 
"""


class JellyDobot(Dobot):
    def __init__(self, port, verbose=False):
        super().__init__(port, verbose)

    def home(self):
        self._start_homing()

    def _start_homing(self, wait=False):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_HOME_CMD
        return self._send_command(msg, wait)
