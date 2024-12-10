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

def read_nocc_from_str(string):
    matches = re.findall(r'Natural occ \[([\d\. e\+\-\n]*)\]', string, re.MULTILINE)
    matches = [np.array(group.strip().split(), dtype=float) for group in matches]
    L = {array.tobytes(): array for array in matches}
    matches = list(L.values())
    return matches
    
def read_S_squared_from_str(string):
    matches = re.findall(r' S\^2 = ([\-\d\.]*)', string, re.MULTILINE)
    matches = np.unique([np.array(group.strip(), dtype=float) for group in matches])
    return matches
    
if __name__=='__main__': 
    with open(sys.argv[1], 'r') as f:
        file_contents = f.read()
        matches = read_nocc_from_str(file_contents) 
        # print(read_S_squared_from_str(file_contents))
        for group in matches:
            print(calc_M_diagnostic(group))     
        
