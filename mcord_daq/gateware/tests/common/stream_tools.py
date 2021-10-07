import random

from cocotb_bus.monitors import BusMonitor
from cocotb_bus.drivers import ValidatedBusDriver
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb.binary import BinaryValue


class StreamMonitor(BusMonitor):

    _signals = ["stb", "eop", "payload_data"]

    def __init__(self, entity, name, clock, **kwargs):
        BusMonitor.__init__(self, entity, name, clock, **kwargs)


    async def _receive_packet(self):
        """We'll be receiving packet until EOP is detected"""
        packet_data = []
        self.log.debug("Waiting for stream packet...")
        clkedge = RisingEdge(self.clock)
        while True:
            await clkedge
            await ReadOnly()
            if self.bus.stb.value:
                packet_data.append(self.bus.payload_data.value.integer)
                if self.bus.eop.value:
                    break
        self.log.debug("Packet received, length: %d", len(packet_data))
        self._recv(packet_data)

    async def _monitor_recv(self):
        while True:
            await self._receive_packet()


class StreamDriver(ValidatedBusDriver):

    _signals = ["stb", "eop", "payload_data"]
    _default_config = {"scatterStb": True}

    def __init__(self, entity, name, clock, config=None, **kwargs):
        ValidatedBusDriver.__init__(self, entity, name, clock, **kwargs)
        self.config = StreamDriver._default_config.copy()

        if config is None:
            config = {}
        for configoption, value in config.items():
            self.config[configoption] = value
            self.log.debug("Setting config option %s to %s", configoption, str(value))

    async def _driver_send(self, values, sync: bool = True):
        self.log.debug("Sending Stream transmission with %d words", len(values))

        # Avoid spurious object creation by recycling
        clkedge = RisingEdge(self.clock)

        word = BinaryValue(n_bits=len(self.bus.payload_data), bigEndian=False)

        # Drive some defaults since we don't know what state we're in
        self.bus.stb <= 0
        self.bus.eop <= 0

        words_to_send = len(values)
        while words_to_send:
            valid_cycle = bool(random.getrandbits(1)) if self.config['scatterStb'] else True
            if valid_cycle:
                await clkedge
                self.bus.stb <= 1
                word.assign(values[-words_to_send])
                self.bus.payload_data <= word
                if words_to_send == 1:
                    self.bus.eop <= 1
                words_to_send -= 1
            else:
                await clkedge
                self.bus.stb <= 0

        await clkedge
        self.bus.stb <= 0
        self.bus.eop <= 0
        word.binstr = "x" * len(self.bus.payload_data)
        self.bus.payload_data <= word

        self.log.debug("Successfully sent stream transmission")
