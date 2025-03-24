#!/usr/bin/env python 
import re, os, pickle, sys
import numpy as np
pickle_dir = sys.argv[1]

lanth = np.unique([re.search(r"subset\d+.(\w+)\.*", file).group(1) for file in os.listdir(pickle_dir) if file[-6:]=='pickle'])
subsets = np.unique([re.search(r"subset(\d+).\w+\.*", file).group(1) for file in os.listdir(pickle_dir) if file[-6:]=='pickle'])
lines = []
header = ['subset', 'lanth', 'spin']
for subset in subsets:
    for La in lanth:
        valid_pickles = [f for f in os.listdir(pickle_dir) if re.search(f'subset{subset}.{La}\.\d*\.pickle', f)]
        for file in valid_pickles:
            data = pickle.load(open(f'{pickle_dir}/{file}', 'rb'))
            
            temp=''
            for key in data.keys():
                if isinstance(data[key], float):
                    if key not in header:
                        header += [f'{key}']
                    temp += f",{data[key]}"
            spin = int(re.findall(r'(\d+)', file)[-1])
            lines += [f'{subset},{La},{spin}' + temp]
            
            # temp_keys, energies = zip(*[(key, data[key]) for key in data if isinstance(data[key], float)])

# print('lanth,spin,CASSCF,MCPDFT,nevpt')
print(','.join(header))
for line in lines:
    print(line)