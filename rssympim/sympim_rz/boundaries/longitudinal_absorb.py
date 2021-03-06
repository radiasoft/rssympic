"""
Boundary condition for particles.

If the particles are outside the longitudinal domain, sets their charge to zero and they become ballistic drifting
particles.

Author: Stephen Webb
"""

import numpy as np
from rssympim.constants import constants as consts
class longitudinal_absorb:

    def __init__(self):
        """
        Radial reflecting boundary condition. Checks the particle data to see if a particle
        has left the domain radially, then flips the sign of its velocity
        """


    def apply_boundary(self, ptcl_data, field_data):

        l_z = field_data.domain_L

        in_bounds_left = np.where(ptcl_data.z < l_z)
        ptcl_data.qOc[in_bounds_left] = ptcl_data.q[in_bounds_left]/consts.c
        out_of_bounds = np.where(ptcl_data.z < 0.)
        ptcl_data.qOc[out_of_bounds] = 0.
        out_of_bounds = np.where(ptcl_data.z > l_z)
        ptcl_data.qOc[out_of_bounds] = 0.
