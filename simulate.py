import sys
import json
import os

import subprocess

dartiq_run_bypass = "./simulate "

output_filename = "simulation_output.md"

test_output = """ ## Simluation Raport
| IP Core name | TB Exist | TB Framework | TB Status | ToDo |
| - | - | - | - | - | 
 """

# ## Tables

# | Option | Description |
# | ------ | ----------- |
# | data   | path to data files to supply the data that will be passed into templates. |
# | engine | engine to be used for processing templates. Handlebars is the default. |
# | ext    | extension to be used for dest files. |




if __name__ == "__main__":
    print("Start Simulations!")

    with open("simulate.json", "r") as f:
        data = json.load(f)

    # print(data)

    if not os.path.exists("temp"):
        status = subprocess.run(["mkdir temp"], shell=True)

    for sim_name in data["simulation_list"]:
        print("INFO: Simulation name: " + sim_name)
        if data["simulation_list"][sim_name]["does_exist"] == "True":
            test_output += sim_name + " | " + \
                data["simulation_list"][sim_name]["does_exist"] + " | " + \
                data["simulation_list"][sim_name]["sim_type"] + " | "
            if data["simulation_list"][sim_name]["sim_type"] == "Migen":
                print("INFO: Migen type simulation.")
                # test_output["simulation"] = sim_name
                # test_output[sim_name]["type"] = data["simulation_list"][sim_name]["sim_type"]

                cmd = [dartiq_run_bypass + data["simulation_list"][sim_name]["tb_path"]]

                subprocess.run(cmd, shell=True)

                test_output += "tb status" + " | " 
                test_output += "tb todo" + " | " 

                test_output += "\n"

            elif data["simulation_list"][sim_name]["sim_type"] == "Cocotb":
                print("INFO: Cocotb type simulation.")

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
                test_output += "\n"
                
            elif data["simulation_list"][sim_name]["sim_type"] == "VerilogTB":
                print("INFO: VerilogTB type simulation.")

                
                test_output += "\n"
        
            else:
                print("ERROR: Test type not supported!")
        else:
            print("INFO: No testbench prepared for: " + sim_name)
            test_output += sim_name + "| False | N/A | N/A | Prepare TB |\n"



    # print(status)

    with open(output_filename, "w") as f:
        print("INFO: Write markdown file: " + output_filename)
        f.write(test_output)





