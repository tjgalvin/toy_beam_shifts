# toy_beam_shifts
A toy around askap beam shifts

This is a simply first pass test of an approach I have suggested,specifically to see if it is a good or bad idea. The question is whether we can exploit IR or optical wavelength surveys to correct our radio-astrometry errors. Since the fundamental physical processes are different across these wavelengths it may not be a simple "nearest neighbour" match. 

This notebook attempts to brute force the problem to obtain a map of likely corrections. 

The basic steps are:
1 - filter the radio catalogue to compact, unresolved and isolated sources
2 - obtain a set of sources from an external caatalogue (here unWISE)
3 - construct a set of realised radio catalogues across a grid of additive angular offsets
4 - Accumulate the angular offsets between each radio source and its nearest neighbour (no radial searching) for each offset point

The hope (belief) is that after an initial cropping of the radio catalogue the remaining components should more often than not have a genuine IR component. Not necessarily all, but a meaningful fraction.

## In the notebbok

There are really two sections in the notebook. The first attempts to align beams onto a common offset by assuming some nominal reference beam is correct. 

Then the process described above is performed *for each beam individually*. The interested results to me are:
1 - the angular offsets per beam a neatly clustered and are not scattered around the origin
2 - ignoring the beam alignment processes introduces scatter to the best matching per beam offsets
