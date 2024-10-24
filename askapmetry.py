"""Utility functions and helper classes to manage toying around with 
ASKAP astrometry
"""

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from astropy.coordinates import SkyCoord
from astropy.table import Table


logger = logging.getLogger("askapmetry")


@dataclass
class Offset:
    """Contains offsets in the RA and Dec directions in arcsec"""
    ra: float
    """Offset in RA direction"""
    dec: float
    """Offset in Dec direction"""

@dataclass
class Catalogue:
    """Represent a per-beam ASKAP component catalogue"""
    beam: int
    table: Table
    """The table loaded"""
    path: Path
    """Original path to the loaded catalogue"""
    center: SkyCoord
    """Rough beam center derived from coordinates of componetns in catalogue"""
    fixed: bool = False
    """Indicates whether beam has been fixed into a place"""
    offset = Offset
    """Per beam offsets, if known, in arcsec"""
    
    def __repr__(self) -> str:
        return f"Catalogue(beam={self.beam}, table={len(self.table)} sources, path={self.path}, fixed={self.fixed})"



def estimate_skycoord_centre(
    sky_positions: SkyCoord, final_frame: str = "fk5"
) -> SkyCoord:
    """Estimate the central position of a set of positions by taking the 
    mean of sky-coordinates in their XYZ geocentric frame. Quick approach
    not intended for accuracy. 

    Args:
        sky_positions (SkyCoord): A set of sky positions to get the rough center of
        final_frame (str, optional): The final frame to convert the mean position to. Defaults to "fk5".

    Returns:
        SkyCoord: The rough center position
    """
    
    xyz_positions = sky_positions.cartesian.xyz
    xyz_mean_position = np.mean(xyz_positions, axis=1)

    mean_position = SkyCoord(
        *xyz_mean_position, representation_type="cartesian"
    ).transform_to(final_frame)

    return mean_position


def filter_table(table: Table) -> np.ndarray:
    """Filter radio components out of an aegean radio catalogue
    based on their distance to neighbouring components and compactness. 

    Args:
        table (Table): Aegean radio component catalogue

    Returns:
        np.ndarray: Boolean array of components to keep. 
    """
    sky_coord = SkyCoord(table["ra"], table["dec"], unit=(u.deg, u.deg))
    
    isolation_mask = sky_coord.match_to_catalog_sky(sky_coord, nthneighbor=2)[1] > (0.01 * u.deg)
    
    ratio = table["int_flux"] / table["peak_flux"]
    ratio_mask = (0.8 < ratio) & (ratio < 1.2)

    return isolation_mask & ratio_mask
  
def get_catalogues(base_path: Path, sbid: int) -> list[Catalogue]:
    """Load in a collection of FITS catalogue produced by aegean. 
    These represent the per-beam catalogues produced by flint. The
    Naming scheme is:
    
    >>> "{str(base_path)}/SB{sbid}.*.beam{beam:02d}.i.MFS.image_comp.fits"

    Args:
        base_path (Path): Path containing the directories to load
        sbid (int): The sbif of the catalogues, used to refine the search

    Returns:
        list[Catalogue]: Loaded catalogues
    """
    catalogues = []
    for beam in range(36):
        path = Path(f"{str(base_path)}/SB{sbid}.*.beam{beam:02d}.i.MFS.image_comp.fits")
        table = Table.read(path)
        
        table_mask = filter_table(table=table)
        sub_table = table[table_mask]

        center = estimate_skycoord_centre(
            SkyCoord(table["ra"], table["dec"], unit=(u.deg, u.deg))
        )
        
        catalogues.append(
            Catalogue(beam=beam, table=sub_table, path=path, center=center)
        )
    return catalogues