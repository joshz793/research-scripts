import re, sys
import numpy as np

def calc_M_diagnostic(n_occ):
    '''
    Calculate a M diagnostic value given an array of natrual orbitals
    M has a lower bound of 0, with no upper bound.
    One would expect a greater multireference characteristic as M -> +inf
    args:
        n_occ: natural orbital occupancy
    returns:
        M: Multireference diagnostic value (from Truhlar Group)
    '''
    unocc = n_occ[n_occ<=0.25]  # Uses natural occupancy = 0.25 as the upper bound for unoccupied orbitals
    if (len(unocc) == 0):   # Default value of 0 if no unoccupied orbitals
        unocc = [0]
    docc = n_occ[n_occ>=1.75] # Natural occupancy = 1.75 as lower bound for doubly occupied orbitals
    if (len(docc) == 0): # Default value of 2 if no doubly occupied orbitals 
        docc = [2]
    somo = n_occ[np.logical_and(n_occ < 1.75, n_occ > 0.25)] # Singly occupied are all other orbitals
    return 0.5 * (2 - min(docc) + sum(np.abs(somo-1)) + max(unocc))

def read_nocc_from_str(string):
    '''
    Uses regex to search for 'Natural occ []' phrases in a string
    Will return only numerically unique lists
    args:
        string: The string to search. Can be a string format of a pyscf output file
    returns:
        matches: a list of the NUMERICALLY UNIQUE Natural occupancies
    '''
    matches = re.findall(r'Natural occ \[([\d\. e\+\-\n]*)\]', string, re.MULTILINE) # Regex across multiple lines, starting from '[' until ']'
    matches = [np.array(group.strip().split(), dtype=float) for group in matches] # Convert string array to float array
    L = {array.tobytes(): array for array in matches} # Use python sets to eliminate exact duplicates
    matches = list(L.values())
    return matches
    
def read_S_squared_from_str(string):
    '''
    Uses regex to search for S^2 values in a string
    Follows the expected output of pyscf output files
    args:
        string: the string to search. Can be a string format of a pyscf output
    returns:
        matches: a numpy array of all detected S^2 values
    '''
    matches = re.findall(r' S\^2 = ([\-\d\.]*)', string, re.MULTILINE)
    matches = [float(group.strip()) for group in matches]
    return matches

# If ran, print M_diagnostic values of the provided file
if __name__=='__main__': 
    with open(sys.argv[1], 'r') as f:
        file_contents = f.read()
        matches = read_nocc_from_str(file_contents) 
        for group in matches:
            print(calc_M_diagnostic(group))     
        
