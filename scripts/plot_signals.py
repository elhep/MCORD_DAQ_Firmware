import json
import sys

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

fs = 20e6



results = json.load(sys.stdin)

fig, axes = plt.subplots(2, 4)
for ch in range(8):
    samples = results[f"ch{ch}"]
    xticks = [1/fs*i for i in range(len(samples))]
    axes[ch // 4, ch % 4].plot(xticks, samples)
    axes[ch // 4, ch % 4].set_title(f"Channel {ch}")
    axes[ch // 4, ch % 4].set_ylim(0, 1024)
plt.show()

