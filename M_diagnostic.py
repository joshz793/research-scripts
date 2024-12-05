import re, sys
import numpy as np
ifile = sys.argv[1]
with open(ifile, 'r') as f:
    file_contents = f.read()
    matches = re.findall(r'Natural occ ([\[\d\. \n]*\])', file_contents, re.MULTILINE)
    matches = [np.array(group[1:-1].strip().split(), dtype=float) for group in matches]
    L = {array.tobytes(): array for array in matches}
    matches = list(L.values())
    
    for group in matches:
        unocc = group[group<=0.25]
        if (len(unocc) == 0):
            unocc = [0]
        docc = group[group>=1.75]
        somo = group[np.logical_and(group < 1.75, group > 0.25)]
        if (len(docc) == 0):
            docc = [2]
        print("M-Value:", 0.5 * (2 - min(docc) + sum(np.abs(somo-1)) + max(unocc))), sep='\t'
