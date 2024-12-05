import re, os, pickle, sys
import numpy as np
pickle_dir = sys.argv[1]

lanth = np.unique([re.search(r"(\w+)\.*", file).group(1) for file in os.listdir(pickle_dir)])

lines = []
for La in lanth:
    valid_pickles = [f for f in os.listdir(pickle_dir) if re.search(f'({La}\.\d*)\.pickle', f)]
    for file in valid_pickles:
        data = pickle.load(open(f'{pickle_dir}/{file}', 'rb'))
        # Just rewriting all the data as variables for convenience
        mol = data['mol']
        mc_mo_coeff = data['mc_mo_coeff']
        mc_ci = data['mc_ci']
        mf_mo_coeff = data['mf_mo_coeff']
        mc_e_tot = data['mc_e_tot']
        mc_e_pdft = data['mc_e_pdft']
        mc_e_nevpt = data['mc_e_nevpt']
        mc_s2 = data['mc_s2']
        spin = int(re.search(f'\d+', file).group(0))
        lines += [f'{La},{spin},{mc_e_tot},{mc_e_pdft},{mc_e_nevpt}']

print('lanth,spin,CASSCF,MCPDFT,nevpt')
for line in lines:
    print(line)