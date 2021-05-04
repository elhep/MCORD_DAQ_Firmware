import threading
import queue
import csv


class SamplesWriter(threading.Thread):

    def __init__(self, daq_channels):
        super().__init__()
        self.daq_channels = daq_channels
        # FIXME: Architectural workaround
        for daq_channel in daq_channels:
            daq_channel["daq"].queue = queue.Queue()
        self.run_data_consumer_service = False
    
    def stop(self):
        self.run_data_consumer_service = False
        self.join()

    def run(self):
        self.run_data_consumer_service = True
        while self.run_data_consumer_service:
            for daq_channel in self.daq_channels:
                try:
                    samples = daq_channel["daq"].queue.get(block=False)
                    # Below does not execute when queue is empty
                    print("Got", len(samples), "from", daq_channel['channel'])
                    self.store_samples(
                        type=daq_channel['type'],
                        channel=daq_channel['channel'],
                        samples=samples)
                except queue.Empty:
                    continue
        
    def store_samples(self, type, channel, trigger_src, trigger_cnt, sample):
        raise NotImplementedError


class CSVSamplesWriter(SamplesWriter):

    def __init__(self, daq_channels, output_path, dialect="excel"):
        super().__init__(daq_channels)
        self.dialect = dialect
        self.output_path = output_path
        self.fieldnames = ["counter", "type", "channel", "l1_idx", "l1_cnt", 
            "sample", "readout"]
        self.counter = 0

        with open(self.output_path, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames, 
                dialect=self.dialect)
            writer.writeheader()

    def store_samples(self, type, channel, samples):
        common = {"counter": self.counter, "type": type, "channel": channel}
        self.counter += 1
        for sample in samples:
            sample.update(common)
        with open(self.output_path, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames, 
                dialect=self.dialect)
            writer.writerows(samples)
