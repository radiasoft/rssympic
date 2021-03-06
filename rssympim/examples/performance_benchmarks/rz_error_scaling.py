"""
This file is for testing the second-order nature of the algorithm.

Author: Stephen Webb
"""

from rssympim.sympim_rz.data import particle_data, field_data
from rssympim.sympim_rz.integrators import integrator
from rssympim.constants import constants
import numpy as np

import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib import pyplot as plt

import time

# species data
charge = constants.electron_charge
mass = constants.electron_mass
speed_of_light = constants.c

# plasma properties
n0 = 1.e18 # cm^-3
omega_p = np.sqrt(4.*np.pi*n0*charge*charge/mass)
k_p = omega_p/speed_of_light

# compute the simulation domain volume
l_r = 4./(k_p/(2.*np.pi)) # cm
l_z = 2./(k_p/(2.*np.pi)) # cm
volume = np.pi*l_r*l_r*l_z

# Domain parameters
n_electrons = n0*volume

# Simulation parameters
n_macro_ptcls = 1000
macro_weight = n_electrons/n_macro_ptcls
n_r_modes = 10
n_z_modes = 10

# Create simulation objects
ptcl_data = particle_data.particle_data(n_macro_ptcls, charge, mass, macro_weight)
fld_data = field_data.field_data(l_z, l_r, n_z_modes, n_r_modes)

def create_init_conds(_ptcl_data, _field_data):

    #_field_data.omega_coords = _ptcl_data.mc[0] * np.ones((n_z_modes, n_r_modes, 2))
    #_field_data.dc_coords = np.zeros((n_z_modes, n_r_modes, 2))

    _ptcl_data.qOc[:] = 0.

    _ptcl_data.r = np.arange(0.1*l_r, 0.9*l_r, 0.8*l_r/n_macro_ptcls)
    _ptcl_data.z = np.arange(0.1*l_z, 0.9*l_z, 0.8*l_z/n_macro_ptcls)
    _ptcl_data.pr = -_ptcl_data.mc * np.arange(0.1, .5, .4 / n_macro_ptcls)
    _ptcl_data.ell = _ptcl_data.weight*constants.electron_mass*constants.c*_ptcl_data.r
    _ptcl_data.pz = _ptcl_data.mc * np.arange(0., 10., 10. / n_macro_ptcls)


create_init_conds(ptcl_data, fld_data)

particle_energies = ptcl_data.compute_ptcl_hamiltonian(fld_data)
field_energies = fld_data.compute_energy()
tot_energy = np.sum(particle_energies) + np.sum(field_energies)

E = []
t = []

E0 = tot_energy

print E0

n_steps = 100
step = 0

dt0 = 10*2*np.pi/np.amax(fld_data.omega)

t0 = time.time()

while step < n_steps:

    # Generate the initial conditions
    create_init_conds(ptcl_data, fld_data)

    # Span dt over decades
    dt = dt0/((1.1)**step)

    # Create the new integrator
    my_integrator = integrator.integrator(dt, fld_data)

    # Integrate a single step
    my_integrator.half_field_forward(fld_data)
    my_integrator.single_step_ptcl(ptcl_data, fld_data)
    my_integrator.half_field_forward(fld_data)

    particle_energies = ptcl_data.compute_ptcl_hamiltonian(fld_data)
    field_energies = fld_data.compute_energy()
    tot_energy = np.sum(particle_energies) + np.sum(field_energies)

    step += 1

    E.append(np.abs(tot_energy-E0)/np.abs(E0))
    t.append(dt)

tf = time.time()

print 'run time =', tf-t0, 'secs'

t = np.amax(fld_data.omega)*np.array(t)/(2.*np.pi)
E = np.array(E)

plt.loglog(t, E, label='error')
plt.loglog(t, (t*t*t)/10**3, label=r'$t^{3}$', alpha=0.5, linestyle='-.')
plt.loglog(t, (t*t)/10**4, label=r'$t^{2}$', alpha=0.5, linestyle='--')
plt.xlabel(r'$(c \Delta t) \times \frac{k_{max.}}{2 \pi}$')
plt.ylabel(r'$\left | \frac{\Delta {H}}{{H}_0} \right |$')
plt.legend()
plt.tight_layout()
plt.show()

