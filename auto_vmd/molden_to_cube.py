from pyscf.tools import cubegen
import sys

molden_infile = sys.argv[1]
from pyscf.tools import molden

mol, mo_energy, mo_coeff, mo_occ, rrep_labels, spins = molden.load(molden_infile)
for i in range(len(mo_coeff[0])):
    cubegen.orbital(mol, '{0}_mo{1}.cube'.format(molden_infile[:-7], i), mo_coeff[:,i])

