






class Channel:

    def __init__(self,
        adc_daq,
        tdc_daq,
        trigger_generator,
        cfd_offset_dac,
        cfd_offset_dac_ch,
        trigger_source):

        pass




# FMC mapping:
# SAS1 | SAS2 | Trig IO | Ref. clk.

# HUB mapping
# SAS1 | SAS2 | CAL in

class McordHub:

    def __init__(self,
        sas1="fmc1@sas1",
        sas2="fmc1@sas2",
        calibration,
        trigger_controller):
        
    def init():
        


class Detector:

    def __init__(self,
        hub,
        hub_ch):
        
        self.cha = Channel()
        self.chb = Channel()

        self.coincidence_controller = RtioCoincidenceTriggerGenerator()

    @property
    def identifiers(self):
        return [
            self.cha.adc_daq.identifier, 
            self.cha.tdc_daq.identifier, 
            self.chb.adc_daq.identifier, 
            self.chb.tdc_daq.identifier
        ]


        


class TriggerController:

    def __init__():

        # Key is an expression for input triggers and value is a channel number
        self.l0_config = {}
        self.l1_config = {}

        # TODO: fill free controllers

        self.l0_free_controllers = {}
        self.l1_free_controllers = {}

        self.output_config = RtioCSR

    def set_coincidence(self, layer, *identifiers):
        assert layer in [0, 1], "Invalid coincidence target!"
        sources = sorted(identifiers)
        expression = "|".join(sources)
        config = getattr(self, f"l{layer}_config")
        free_controllers = getattr(self, f"l{layer}_free_controllers")
        if expression not in config:
            if len(free_controllers) == 0:
                raise RuntimeError(f"l{layer} has no more free controllers!")
            controller = free_controllers.pop()
            controller.enable_source(*sources)
            config[expression] = controller
            return controller
        else:
            return config[expression]

    def set_detector_coincidence(self, *detectors):
        # This function operates on L1
        identifiers = [d.coincidence_controller.identifier for d in detectors]
        controller = self.set_coincidence(1, *identifiers)
        return controller

    def set_trigger_source(self, source, *identifiers):
        for identifier in identifiers:
            getattr(self.output_config, f"{identifier}_output_select").write(source.index)

    def enable_output(self, state, *identifiers):
        for identifier in identifiers:
            getattr(self.output_config, f"{identifier}_output_enable").write(state)

    def create_coincidence_group(self, *detectors):
        controller = self.set_detector_coincidence(*detectors)
        identifiers = []
        for detector in detectors:
            identifiers.append(detector.identifiers)
        self.set_trigger_source(controller, *identifiers)


def general_init():
    # HUB / Detector specific
    for idx, detector in enumerate(self.hub0.detectors):
        controller = self.trigger_controller.set_coincidence(
            0,  # layer 
            detector.cha.trigger_generator.rising_edge, 
            detector.chb.trigger_generator.rising_edge)
        detector.coincidence_controller = controller
        
    
def setup():
    self.trigger_controlller.create_coincidence_group(
        hub0.detectors[0], hub0.detectors[1]
    )
    
    
    
    