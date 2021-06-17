import sys
import json
import os

import subprocess



if __name__ == "__main__":
    print("Start Simulations!")

    with open("simulate.json", "r") as f:
        data = json.load(f)

    print(data)


    for sim_name in data["simulation_list"]:
        print(sim_name)
        if data["simulation_list"][sim_name]["sim_type"] == "Migen":
            print("Migen type simulation")
            # cmd = ["dartiq",\
            #     "run", \
            #     "--no-stdin",\
            #     '\"python',
            #     './modules/ELHEP_Cores/elhep_cores/cores/dsp/baseline_avg.py\"']


            # cmd = ["ls"]

            # cmd = ["dartiq", "run", "\"python ./modules/ELHEP_Cores/elhep_cores/cores/dsp/baseline_avg.py\""]

            # cmd = "dartiq run --no-stdin \"python ./modules/ELHEP_Cores/elhep_cores/cores/dsp/baseline_avg.py\"".split()

            cmd = "dartiq run \"echo test\"".split()
            print(cmd)

            pwd = os.path.dirname(os.path.realpath(__file__)) 

            print(pwd)
            status = subprocess.run(cmd, shell=True)

    print(status)
