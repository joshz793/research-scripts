from pyscf.tools import cubegen
from pyscf.tools import molden
import sys

molden_infile = sys.argv[1]
mol, mo_energy, mo_coeff, mo_occ, rrep_labels, spins = molden.load(molden_infile)

if len(sys.argv) > 2:
    mo_idx = []
    idx = sys.argv[2:]
    for v in idx:
        try: # If can be converted to int, then is a lone index
            mo_idx.append(int(v)-1)
        except ValueError:  # Otherwise, check if is range
            try:
                start = v.split('-')[0].strip()
                stop = v.split('-')[-1].strip()
                for id in range(int(start)-1,int(stop)): mo_idx.append(id)
            except ValueError:
                print("Could not understand {0}".format(v))
            except:
                print("Some other error occurred")           
else:   # If no specified index, then make cube for all orbitals
    mo_idx = range(len(mo_coeff[0]))
    
for i in mo_idx:
    cubegen.orbital(mol, '{0}_mo{1}.cube'.format(molden_infile[:-7], i), mo_coeff[:,i])

