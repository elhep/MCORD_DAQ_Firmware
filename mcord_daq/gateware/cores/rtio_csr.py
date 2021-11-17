from migen import *
from artiq.gateware.rtio import rtlink
from artiq.gateware.rtio.channel import Channel
from elhep_cores.helpers.ddb_manager import HasDdbManager


class _RTField:
    def __init__(self, name, signal=None, width=1, reset=0, readonly=False, 
            description="", values=None):        
        self.name = name
        self.stb = Signal()
        self.signal = None
        if signal is None:
            if width > 0:
                self.signal = Signal(width, reset=reset)
                self.width = width
            elif width == 0:
                assert len(signal) == 1
                self.stb = signal
            else:
                raise ValueError("Invalid RTField width") 
        if signal is not None:
            self.signal = signal
            self.width = len(signal)
        self.description = description
        self.values = values
        self.readonly = readonly
        
    def get_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "values": self.values,
            "width": self.width,
            "readonly": self.readonly
        }


class RTStatus(_RTField):
    def __init__(self, name, signal, description="", values=None):
        super().__init__(name, signal=signal, readonly=True, 
                         description=description, values=values)


class RTStorage(_RTField):
    def __init__(self, name, signal=None, width=1, reset=0, description="", 
            values=None):
        super().__init__(name, signal, width, reset, False, description, values)


class RTReg(Module, HasDdbManager):
    
    def __init__(self, fields, identifier):
        iface_width = max([f.width for f in fields])
        iface_adr_width = len(fields).bit_length() + 1

        assert 0 <= iface_width <= 32
        assert 0 < iface_adr_width <= 8
        
        self.rtlink = rtlink.Interface(
            rtlink.OInterface(data_width=iface_width, address_width=iface_adr_width),
            rtlink.IInterface(data_width=iface_width, timestamped=False))

        write_enable = self.rtlink.o.address[0]
        address = self.rtlink.o.address[1:]      
        
        # Write
        data_signals = []
        for idx, field in enumerate(fields):
            assert field.name not in self.__dict__ or f"{field.name}_stb" not in self.__dict__, \
                "Field name must be unique"
            # stb is always available
            stb = Signal()
            setattr(self, f"{field.name}_stb", stb)
            statements = [stb.eq(1)]
            if field.signal:
                setattr(self, field.name, field.signal)
                if not fiel.readonly:
                    statements += [sig.eq(self.rtlink.o.data)]
                data_signals.append(sig)
            else:
                data_signals.append(Constant(0, iface_width))
            self.sync.rio_phy += [
                stb.eq(0),
                If(self.rtlink.o.stb & write_enable & (address == idx),
                    *statements
                )
            ]
        
        # Read
        data_signals_array = Array(data_signals)
        self.sync.rio_phy += [
            self.rtlink.i.stb.eq(0),
            If(self.rtlink.o.stb & ~write_enable,
               self.rtlink.i.stb.eq(1),
               self.rtlink.i.data.eq(data_signals[address]))
        ]

    if identifier is not None:
        self.add_rtio_channels(
            channel=Channel.from_phy(self),
            device_id=identifier,
            module="elhep_cores.coredevice.rtio_csr",
            class_name="RTIOCSR",
            arguments={
                "regs": [field.get_json() for field in fields]
            })