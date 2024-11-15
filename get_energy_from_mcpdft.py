import sys, os
filename = "mcpdft.out"

casscf_key = 'CASSCF'
mcpdft_key = 'MC-PDFT'

data = {'spin':[], 'CASSCF':[], 'MCPDFT':[], 'convergence':[]}
spin = None
with open(filename, 'r') as f:
    line = ''
    while line != None:
        line = next(f, None)
        if line == None:
            break
        if len(line.split()) == 0:
            continue
        
        if line[:5] == 'CAS (':
            alpha_e = int(line.split('+')[0].split('(')[-1][:-1])
            beta_e = int(line.split('+')[1].split(',')[0][:-1])
            spin = alpha_e - beta_e
            data["spin"] += [spin]
        elif line.split()[0].strip() == casscf_key:
            if '=' not in line:
                continue
            if spin == None:
                print("No spin found before energy, check output file")
                break
            data['CASSCF'] += [float(line.split('=')[-1].strip().split()[0].strip())]
        elif line.split()[0].strip() == mcpdft_key:
            if '=' not in line:
                continue
            if spin == None:
                print("No spin found before energy, check output file")
                break
            data['MCPDFT'] += [float(line.split(',')[0].split('=')[-1].strip().split()[0].strip())]
        elif line[:13] == '1-step CASSCF':
            split_line = line.split()
            if split_line[2] == 'converged':
                data['convergence'] += [int(split_line[4])]
            elif split_line[2] == 'not':
                data['convergence'] += ['NaN']
        
import csv
with open("energy.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(data.keys())
    w.writerows(zip(*[data[i] for i in data.keys()]))