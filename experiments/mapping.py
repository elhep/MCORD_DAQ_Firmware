# FMC Connectors: (FP view) J13 | J12 | TRIG | CLK IN
# SAS MCX: (TOP view, from right) J7 | J6

adc_mapping = {
    0: 3, 
    1: 2,
    2: 1,
    3: 0,
    4: 7,
    5: 6,
    6: 5,
    7: 4
}

def channel_mapping(channel):
    return {
            "channel": channel,
            "tdc": channel // 4,
            "tdc_daq": channel % 4,
            "cfd_dac": channel // 8,
            "cfd_dac_ch": channel % 8,
            "adc": channel // 8,
            "adc_daq": adc_mapping[channel % 8],
        }

fmc_mapping = {"j12": {}, "j13": {}}

for connector in range(2):
    for ch in range(4):
        channel = 8*connector + ch*2
        fmc_mapping[f"j{12+connector}"][f"tx{ch}"] = channel_mapping(channel+0)
        fmc_mapping[f"j{12+connector}"][f"rx{ch}"] = channel_mapping(channel+1)

#### 

sas_mcx_adapter_mapping = {"j6": {}, "j7": {}}

for connector in range(2):
    for ch in range(4):
        sas_mcx_adapter_mapping[f"j{6+connector}"][f"tx{ch}"] = f"A{4*connector+ch+1}"
        sas_mcx_adapter_mapping[f"j{6+connector}"][f"rx{ch}"] = f"B{4*connector+ch+1}"

####

import re

def connect(mapping, *args):
    output = {}
    for arg in args:
        match_result = re.findall(r'(\w+)->(\w+)', arg)
        if not match_result:
            raise ValueError(f"Invalid connector mapping ({arg})!")
        from_con, to_con = match_result[0]

        if from_con not in mapping:
            raise ValueError(f"FROM connector ({from_con}) not found in given mapping!")

        if to_con not in fmc_mapping:
            raise ValueError(f"TO connector ({to_con}) not found in FMC mapping!")

        for element in mapping[from_con]:
            output[mapping[from_con][element]] = fmc_mapping[to_con][element]
    
    return output


if __name__ == "__main__":
    from pprint import pprint
    mapping = connect(sas_mcx_adapter_mapping, "j6->j13")
    pprint({"A4":mapping["A4"]})
    pprint({"B4":mapping["B4"]})
    