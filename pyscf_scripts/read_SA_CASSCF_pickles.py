#!/usr/bin/env python 
import re, os, pickle, sys
import numpy as np
from collections.abc import Iterable
pickle_dir = sys.argv[1]

lanth = np.unique([re.search(r"subset\d+.(\w+)\.*", file).group(1) for file in os.listdir(pickle_dir) if file[-6:]=='pickle'])
subsets = np.unique([re.search(r"subset(\d+).\w+\.*", file).group(1) for file in os.listdir(pickle_dir) if file[-6:]=='pickle'])
lines = []
header = ['subset', 'lanth']
for subset in subsets:
    for La in lanth:
        valid_pickles = [f for f in os.listdir(pickle_dir) if re.search(f'subset{subset}.{La}.SA-CASSCF.pickle', f)]
        for file in valid_pickles:
            data = pickle.load(open(f'{pickle_dir}/{file}', 'rb'))
            # print(type(data['mc_e_states']))
            temp=''
            for key in data.keys():
                field = data[key]
                if isinstance(data[key], Iterable):
                    field = np.array(field)
                if isinstance(field, np.ndarray) and len(field.shape) == 1:
                    header += [f'{key}{n}' for n in range(field.shape[0]) if f'{key}{n}' not in header]
                    temp += ','.join([f"{d}" for d in field])
            lines += [f'{subset},{La},' + temp]
            # temp_keys, energies = zip(*[(key, data[key]) for key in data if isinstance(data[key], float)])

# print('lanth,spin,CASSCF,MCPDFT,nevpt')
print(','.join(header))
for line in lines:
    print(line)