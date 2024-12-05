import sys
import numpy as np
import pickle
from pyscf import gto, scf, mcscf, mcpdft, mrpt, lib
from mrh.my_pyscf.fci import csf_solver
from mrh.my_pyscf.gto import ANO_RCC_VDZP
from pyscf.mcscf import avas

def struct(xyz,spin=0,charge=0, basis=ANO_RCC_VDZP):
    mol = gto.Mole()
    mol.atom = xyz
    mol.basis = basis
    mol.spin=spin
    mol.charge=charge
    mol.verbose=4
    mol.max_memory = 960000
    mol.build()
    return mol

def runmf(mol, max_cycle=100, density_fit=True):
    if not density_fit:
        mf = scf.UHF(mol).sfx2c1e()
    else:
        mf = scf.UHF(mol).sfx2c1e().density_fit()
    mf.max_cycle = max_cycle
    mf.init_guess='atom'
    mf.kernel()
    mf.analyze()
    dm = mf.make_rdm1()
    
    # if the first order mf has not converged then we are using the 
    # second order method
    # We are also using first order dm as init guess for the second order.
    if not mf.converged:
        mf = mf.newton()
        mf.kernel(dm)
        mf.analyze()
    return mf

def get_initguess(mol, mf, Lanth='La'):
    mo_coeff = avas.kernel(mf, [f'{Lanth} 4f', f'{Lanth} 5d', f'{Lanth} 6s'],with_iao=True, minao=mol.basis)[2]
    return mo_coeff

def getguessfromsmallerCAS(mf, mo_coeff, spin, nelecas, ncas=7):
    alpha, beta = int(nelecas)//2 + int(np.ceil(spin/2)), int(nelecas)//2 - int(spin)//2
    mc = mcscf.CASSCF(mf, ncas, (alpha, beta))
    mc.fcisolver = csf_solver(mol, smult=int(spin+1))
    mc.max_cycle_macro = 500
    mc.natorb = True
    mc.kernel(mo_coeff)
    assert mc.converged, "Even smaller CAS didn't converge"
    return mc.mo_coeff

def runCASSCF(mf, mo_coeff, spin, ncas, nelecas, La='La', recur=False):
    alpha, beta = int(nelecas)//2 + int(np.ceil(spin/2)), int(nelecas)//2 - int(spin)//2
    mc = mcscf.CASSCF(mf, ncas, (alpha, beta))
    mc.fcisolver = csf_solver(mol, smult=int(spin+1))
    mc.max_cycle_macro = 150
    mc.chkfile = f'{La}.{spin}.chk'
    mc.ah_level_shift = 0.5
    mc.conv_tol = 1e-8
    mc.natorb = True
    mc.kernel(mo_coeff)
    mc.analyze()
    if not mc.converged and not recur:
        mo_coeff = getguessfromsmallerCAS(mf, mo_coeff, spin, nelecas, ncas=alpha+1) # effectively single-reference + virtual orbital
        return runCASSCF(mf, mo_coeff, spin, ncas=ncas, nelecas=nelecas, La=La, recur=True)
    else:
        assert mc.converged, "Did not converge Minimal CAS"
    s2 = mc.fcisolver.spin_square(mc.ci, mc.ncas, mc.nelecas)
    mc_rdm1 = mc.make_rdm1()
    with open(f'{La}.{spin}.mc.pickle', 'wb') as f:
        pickle.dump({"mc_rdm1": mc_rdm1}, f)
    return mc, s2

def runMCPDFT(cas, ot='tPBE'):
    mc = mcpdft.CASCI(cas, ot, cas.ncas, cas.nelecas)
    e_tot = mc.kernel()[0]
    return e_tot

def savemolden(mc, La='La', spin=0):
    from pyscf.tools import molden
    molden.from_mo(mol, f'{La}.{spin}.molden', mc.mo_coeff[:, mc.ncore:mc.ncore+mc.ncas])

def runNEVPT2(mc):
    nevpt = mrpt.NEVPT(mc)
    ept = nevpt.kernel()
    etot = mc.e_tot + ept
    return etot

def runGivenSpin(mf, mo_coeff, spin, ncas, nelecas, La='La'):
    mc, s2 = runCASSCF(mf,mo_coeff, spin, ncas, nelecas, La=La)
    e_mcscf = mc.e_tot
    savemolden(mc, La=La, spin=spin)
    with lib.temporary_env(mc):
        e_pdft = runMCPDFT(mc)
    with lib.temporary_env(mc):
        e_nevpt = runNEVPT2(mc)
    with open(f'{La}.{spin}.pickle', 'wb') as f:
        thisdata={  "mol": mol,
                    "mc_mo_coeff": mc.mo_coeff,
                    "mc_ci": mc.ci,
                    "mf_mo_coeff": mf.mo_coeff,
                    "mc_e_tot": e_mcscf,
                    "mc_e_pdft": e_pdft,
                    "mc_e_nevpt": e_nevpt,
                    "mc_s2": s2}
        pickle.dump(thisdata, f)
    return mc.mo_coeff, s2

if __name__ == '__main__':
    xyz_file=sys.argv[1]
    ncas=int(sys.argv[2])
    nelecas=int(sys.argv[3])
    charge=int(sys.argv[4])
    La = sys.argv[5] # Write an assert to make the La atom ...
    
    possible_spins = list(range(min(nelecas, ncas) - max(0, nelecas-ncas), -1, -2))
    mol = struct(xyz_file, spin=possible_spins[0], charge=charge, basis=ANO_RCC_VDZP)
    mf = runmf(mol)
    mf_mo_occ = mf.mo_occ
    mf_rdm1 = mf.make_rdm1()
    with open(f'{La}.{possible_spins[0]}.mf.pickle', 'wb') as f:
        pickle.dump({"mf_mo_occ":mf_mo_occ, "mf_rdm1":mf_rdm1}, f)
    mo_coeff = get_initguess(mol, mf, Lanth=La)

    for spin in possible_spins:
        
        # Using the smaller CAS space calculation for the mo_coeffs
        if spin == possible_spins[0]:
            mo_coeff = getguessfromsmallerCAS(mf, mo_coeff, spin, nelecas=nelecas, ncas=spin)

        print(f"Running {xyz_file} with {La} spin {spin} and charge {charge} with {ncas} active orbitals and {nelecas} active electrons")
        mo_coeff, s2 = runGivenSpin(mf, mo_coeff, spin, ncas, nelecas, La=La)
