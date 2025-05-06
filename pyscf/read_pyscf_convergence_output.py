import sys, os, re

filename = sys.argv[1]
if len(sys.argv) > 2:
    out_filename = sys.argv[2]
else:
    out_filename = "output.png"
data = {}
data['iter'] = []
prev_was_macro = False
conv_tol = 0
conv_tol_grad = 0
with open(filename, 'r') as f:
    line = next(f, None)
    while line is not None:
        if line[:9] == 'conv_tol ':
            conv_tol = float(line.split('=')[-1].strip())
        if line[:17] == 'Set conv_tol_grad':
            conv_tol_grad = float(line.split()[-1].strip())
        
        if line[:10] == 'macro iter' or prev_was_macro:
            key = None
            value = None
            temp_data = [i for i in re.split(',|\(|\)|=|\s', line[10:].strip()) if i != '']
            if not prev_was_macro:
                if int(temp_data[0]) in data['iter']:   # macro iter = 1 -> new simulation. Saving only last simulation
                    data = {}
                    data['iter'] = []
                data['iter'].append(int(temp_data[0]))
            
            for i in temp_data[0:]:
                # Dirty code, the re.split from above results in alternating numbers/str
                # the str are *generally* paired with an adjacent number 
                try:
                    value = float(i)
                except ValueError:
                    key = i
                if key is not None and value is not None:
                    if key not in data: # new dict entry if not exist
                        data[key] = []
                    data[key].append(value)
                    key = None
                    value = None
            prev_was_macro = not prev_was_macro # since simulation data continues on each line after a macro iter line
        line = next(f, None)

import matplotlib.pyplot as plt
import numpy as np
num_plots = len(data.keys())-1
n_row = n_col = int(np.ceil(np.sqrt(num_plots)))
keys = np.resize(np.array(list(data.keys()))[1:], (n_row,n_col))
fig, axes = plt.subplots(n_row, n_col, figsize=(n_col*4, n_row*4))

keys_plotted = 0
for row, temp_keys in zip(axes, keys):
    for ax, key in zip(row, temp_keys):
        if keys_plotted >= num_plots:
            break
        y = data[key]
        if key.upper() == 'DE':
            y = np.abs(y)
            ax.set_title('|{0}|'.format(key), fontsize=12)
        else:
            ax.set_title(key, fontsize=12)
        ax.plot(data['iter'], y)
        # Switch to log-scale if the y-range is very large
        data_mult_range = max(y)/(min(y)+0.00000000001)
        if (min(y) > 0) and (data_mult_range > 100 or data_mult_range < 0.1):
            ax.set_yscale('log')
        
        # If the latter half is significantly different than the initial points
        # -> focus on the latter half
        # data_range = max(y) - min(y) + 0.00000000001 
        # latter_data = y[len(y)//2:]
        # latter_data_range = max(latter_data) - min(latter_data) + 0.00000000001 # very small number to avoid Zero-division
        # if latter_data_range / data_range < 0.25: 
        #     ax.set_ylim((0.9 * min(latter_data), 1.1 * max(latter_data)))
        
        if key.upper() == 'DE':
            ax.hlines(10**-8,min(data['iter']), max(data['iter']), 'r')
        if 'grad' in key.lower():
            ax.hlines(conv_tol_grad,min(data['iter']), max(data['iter']), 'r')
        keys_plotted += 1

fig.supxlabel("Macro iter", fontsize=16)
fig.suptitle("Convergence data from {0}".format(filename), fontsize=20)
fig.tight_layout()
fig.savefig("{0}".format(out_filename))
