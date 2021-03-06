###############################################################################
# Copyright Daniel Davies, Adam J. Jackson, Keith T. Butler (2016)            #
#                                                                             #
# This file is part of SMACT: properties.py is free software: you can         #
# redistribute it and/or modify it under the terms of the GNU General Public  #
# License as published by the Free Software Foundation, either version 3 of   #
# the License, or (at your option) any later version.  This program is        #
# distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;   #
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A       #
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.   #
# You should have received a copy of the GNU General Public License along     #
# with this program.  If not, see <http://www.gnu.org/licenses/>.             #
#                                                                             #
###############################################################################

from __future__ import print_function
from __future__ import division
from builtins import map
from builtins import input
from builtins import range
from past.utils import old_div
import smact
from numpy import sqrt, product

def eneg_mulliken(element):
    """Get Mulliken electronegativity from the IE and EA

    Arguments:
        symbol (smact.Element or str): Element object or symbol

    Returns:
        mulliken (float): Mulliken electronegativity

    """
    if type(element) == str:
        element = smact.Element(element)
    elif type(element) != smact.Element:
        raise Exception("Unexpected type: {0}".format(type(element)))

    mulliken = old_div((element.ionpot+element.e_affinity),2.0)

    return mulliken


def band_gap_Harrison(anion, cation, verbose=False,
                      distance=None, elements_dict=None):

    """
    Estimates the band gap from elemental data.

    The band gap is estimated using the principles outlined in
    Harrison's 1980 work "Electronic Structure and the Properties of
    Solids: The Physics of the Chemical Bond".

    Args:
        Anion (str): Element symbol of the dominant anion in the system.

        Cation (str): Element symbol of the the dominant cation in the system.
        Distance (float or str): Nuclear separation between anion and cation
                i.e. sum of ionic radii.
        verbose: An optional True/False flag. If True, additional information
                is printed to the standard output. [Defult: False]
        elements_dict (dict): Element symbol keys with smact.Element
                objects values. This may be provided to prevent
                excessive reading of data files.

    Returns (float): Band gap in eV.

    """

    # Set constants
    hbarsq_over_m = 7.62

    # Get anion and cation
    An = anion
    Cat = cation
    d = float(distance)

    # Get elemental data:
    elements_dict = smact.element_dictionary((An, Cat))
    An, Cat = elements_dict[An], elements_dict[Cat]

    # Calculate values of equation components
    V1_Cat = old_div((Cat.eig - Cat.eig_s),4)
    V1_An = old_div((An.eig - An.eig_s),4)
    V1_bar = old_div((V1_An + V1_Cat),2)
    V2 = 2.16 * hbarsq_over_m / (d**2)
    V3 = old_div((Cat.eig - An.eig),2)
    alpha_m = old_div((1.11*V1_bar),sqrt(V2**2 + V3**2))

    # Calculate Band gap [(3-43) Harrison 1980 ]
    Band_gap = (old_div(3.60,3))*(sqrt(V2**2 + V3**2))*(1-alpha_m)
    if verbose:
        print("V1_bar = ", V1_bar)
        print("V2 = ", V2)
        print("alpha_m = ", alpha_m)
        print("V3 = ", V3)

    return Band_gap


def compound_electroneg(verbose=False, elements=None, stoichs=None,
                                                source='Mulliken'):

    """Estimate electronegativity of compound from elemental data.

    Uses Mulliken electronegativity by default, which uses elemental
    ionisation potentials and electron affinities. Alternatively, can
    use Pauling electronegativity, re-scaled by factor 2.86 to achieve
    same scale as Mulliken method (Nethercot, 1974)
    DOI:10.1103/PhysRevLett.33.1088 .

    Geometric mean is used (n-th root of product of components), e.g.:

    X_Cu2S = (X_Cu * X_Cu * C_S)^(1/3)

    Args:
    elements: A list of elements given as standard elemental symbols.
    stoichs: A list of stoichiometries, given as integers or floats.
    verbose: An optional True/False flag. If True, additional information
    is printed to the standard output. [Default: False]
    elements_dict: Dictionary of smact.Element objects; can be provided to
    prevent multiple reads of data files
    source: String 'Mulliken' or 'Pauling'; type of Electronegativity to
    use. Note that in SMACT, Pauling electronegativities are
    rescaled to a Mulliken-like scale.

    Returns:
    Electronegativity: Estimated electronegativity as a float.
    Electronegativity is a dimensionless property.

    Raises:
    (There are no special error messages for this function.)
    """
    if type(elements[0]) == str:
        elementlist = [smact.Element(i) for i in elements]
    elif type(elements[0]) == smact.Element:
        elementlist = elements
    else:
        raise Exception("Please supply a list of element symbols or SMACT Element objects")

    stoichslist = stoichs
    # Convert stoichslist from string to float
    stoichslist = list(map(float, stoichslist))

    # Get electronegativity values for each element

    if source == 'Mulliken':
        elementlist = [old_div((el.ionpot+el.e_affinity),2.0)
                       for el in elementlist]

    elif source == 'Pauling':
        elementlist = [(2.86 * el.pauling_eneg)
                       for el in elementlist]
    else:
        raise Exception("Electronegativity type '{0}'".format(source),
                        "is not recognised")

    # Print optional list of element electronegativities.
    # This may be a useful sanity check in case of a suspicious result.
    if verbose:
        print("Electronegativities of elements=", elementlist)

    # Raise each electronegativity to its appropriate power
    # to account for stoichiometry.
    for i in range(0, len(elementlist)):
        elementlist[i] = [elementlist[i]**stoichslist[i]]

    # Calculate geometric mean (n-th root of product)
    prod = product(elementlist)
    compelectroneg = (prod)**(old_div(1.0,(sum(stoichslist))))

    if verbose:
        print("Geometric mean = Compound 'electronegativity'=", compelectroneg)

    return compelectroneg
