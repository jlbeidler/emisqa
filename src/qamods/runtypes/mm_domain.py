from __future__ import print_function
from qamods.data_file import DataFile
import numpy as np
from qamods.species_array import SpeciesArray
import sys

def getDict(speciesList, fileName, allHours = False, grid = '', gridDesc = '', ignoreSpec = False, inln = False, interpolate = False, layer = '', region = '', 
	stacks = False, ptsr = False, inFormat = 'NCF', verbosity = False, zipDict = {}):
	'''
	Sums up every grid cell for a day for each species.
	'''
	if not fileName: 
		raise ValueError('You must specify an input filename using the -f argument.')
	if region: 
		raise ValueError('This run type does not support grid to fips conversion.  Please remove -e argument from command line.')

	file1 = DataFile(fileName, verbosity, inFormat, ptsr, zipDict)

	print('Running max/min')
	outDict = dict()

	for speciesName in speciesList:
		if verbosity: 
			print('Running max/min for species: %s' %speciesName)

		if speciesName not in file1.speciesList and ignoreSpec:
			print('WARNING: The species %s does not exist in the file %s.  Skipping.' %(speciesName, file1))
			continue	

		array1 = SpeciesArray(file1.sumVal(speciesName, layer, allHours), speciesName)
		mmVals = array1.maxMin()
		outFile.write('For species %s\n' %speciesName)
		outFile.write('Min Value: %s   Max Value: %s\n' %(mmVals[0], mmVals[1]))

	sys.exit(0)

