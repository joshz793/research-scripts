import re, sys
import numpy as np

def calc_M_diagnostic(n_occ):
    unocc = n_occ[n_occ<=0.25]
    if (len(unocc) == 0):
        unocc = [0]
    docc = n_occ[n_occ>=1.75]
    somo = n_occ[np.logical_and(n_occ < 1.75, n_occ > 0.25)]
    if (len(docc) == 0):
        docc = [2]
    return 0.5 * (2 - min(docc) + sum(np.abs(somo-1)) + max(unocc))

def read_nocc_from_outfile(ifile):
    with open(ifile, 'r') as f:
        file_contents = f.read()
        matches = re.findall(r'Natural occ ([\[\d\. \n]*\])', file_contents, re.MULTILINE)
        matches = [np.array(group[1:-1].strip().split(), dtype=float) for group in matches]
        L = {array.tobytes(): array for array in matches}
        matches = list(L.values())
        return matches
    
if __name__=='__main__': 
    matches = read_nocc_from_outfile(sys.argv[1])   
    for group in matches:
        print(calc_M_diagnostic(group))     
        
