import sys
import json
import os

import subprocess

dartiq_run_bypass = "./simulate "

test_output = {}

if __name__ == "__main__":
    print("Start Simulations!")

    with open("simulate.json", "r") as f:
        data = json.load(f)

    print(data)

    if not os.path.exists("temp"):
        status = subprocess.run(["mkdir temp"], shell=True)

    for sim_name in data["simulation_list"]:

        print("INFO: Simulation name: " + sim_name)
        if data["simulation_list"][sim_name]["sim_type"] == "Migen":
            print("INFO: Migen type simulation.")
            test_output["simulation"] = sim_name
            # test_output[sim_name]["type"] = data["simulation_list"][sim_name]["sim_type"]

            cmd = [dartiq_run_bypass + data["simulation_list"][sim_name]["tb_path"]]

            subprocess.run(cmd, shell=True)

        if data["simulation_list"][sim_name]["sim_type"] == "Cocotb":

            # cmd = [dartiq_run_bypass + data["simulation_list"][sim_name]["tb_path"]]

            # subprocess.run(cmd, shell=True)
            subprocess.run("cd modules/ELHEP_Cores/elhep_cores/cores/dsp/tests; make", shell=True)

            # cmd.append("cd temp;")
            # cmd.append("ls;")

            # cmd.append("dartiq run --no-stdin \"python ../modules/ELHEP_Cores/elhep_cores/cores/dsp/baseline_avg.py\"")


            # pwd = os.path.dirname(os.path.realpath(__file__)) 

            # print(pwd)
            # status = subprocess.run(["ls"], shell=True)
            # status = subprocess.run(["ls; cd temp; ls; dartiq run --no-stdin \"python ../modules/ELHEP_Cores/elhep_cores/cores/dsp/baseline_avg.py\" "], shell=True)
            # 

    # print(status)







