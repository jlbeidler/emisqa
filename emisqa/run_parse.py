from __future__ import print_function
from emisqa.helpers import check_ev, conv2greg
from emisqa.default_paths import *
from optparse import OptionParser,OptionGroup
from emisqa.data_file import DataFile
from emisqa.dateloop import inday as dl
from emisqa.inline.stack_group import StkGrp
import os.path
from sys import exit
from emisqa.io.fauxio import Grid

### Main

def listRunTypes():
    '''
    Lists the available run types and syntax.
    '''
    print('''
    \n\t\tRun types for the pyQA script.\n\t\t      ------------  \n
    pe: percent error run between two files and the specified species.  Requires two files listed with the -f option.
    rd: raw difference run between two files and the specified species.  Requires two files listed with the -f option.
    add: adds together two files and the specified species. Returns CSV.  Requires two files listed with the -f option.
    dv: dumps the daily value or timestep sum of a specified file.  Requires one file listed with the -f option.
    sum: sums up a group of files. Requires case, sector, speciation, input path, grid, GSDATE, and rundays.
    avg: averages a group of files over the number of days. Requires case, sector, speciation, input path, grid, GSDATE, and rundays.
    domain: writes the daily domain of a file.  Returns as one line CSV.  Requires one file listed with the -f option.
    mm: gives the maximum and minimum species values for a file.  Requires one file listed with the -f option.
    dump: raw dump of a gridded file.  Requires one file with the -f option.
    dh: Dump hourly data from a gridded file. Useful for type conversions.\n
    ''')
    exit(1)

def get_opts():
    # Handle command line arguments and options.
    parser = OptionParser(usage = 'usage: %prog [options] OUTFILE RUNTYPE')
    outputGroup = OptionGroup(parser, "Output File Configuration Options")
    loopGroup = OptionGroup(parser, "Options Required for sum and avg Methods")
    regionGroup = OptionGroup(parser, "Options Required for Region Output","Output type must be set to CSV or left default")
    parser.add_option('-s', '--speciesname', dest='species_name', help='List of species to process.  Ex. -s SPEC1,SPEC2,...', default='')
    parser.add_option('-a', '--allspecies', action='store_true', dest='all_species', help='Run for all species.', default=False)
    parser.add_option('-l', '--listruns', action='store_true', dest='listRuns', help='List run types.', default=False) 
    parser.add_option('-f', '--file', dest='file_name', help='Specify a file or a list of up to two files for access.', metavar='FILE', default='')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbosity', help='Give more information during run.', default=False)
    parser.add_option('-i', '--inline', action='store_true', dest='inln', help='Use inline input files with stack groups rather than 2D', default=False)
    parser.add_option('-g', '--stack-groups', dest='stack_file', help='Explicitly set stack groups file location.  Set to default path when looping with -i option.', default = '')
    parser.add_option('-c', '--informat', dest='informat', help='Input file type. Specify NCF, CSV, or UAM.', default='NCF', metavar='INTYPE')
    parser.add_option('--camx-ptsr', action='store_true', dest='ptsr', help='Use PTSOURCE CAMx emissions format as input.', default=False)
    parser.add_option('--layer', dest='layer', help='Specify an individual layer.  Defaults to flatten all layers.', metavar='#', default='')
    parser.add_option('--ignore-missing', action='store_true', dest='ignore_spec', help='Ignore missing input species instead of producing fatal error.  May produce inaccurate results.', default=False)
    parser.add_option('--interpolate', action='store_true', dest='interpolate', help='Average between hours to get interpolated results for CAMx comparison.', default=False)
    parser.add_option('--mp', dest='threads', help='Threads to use. Defaults to 1.', default='1')
    regionGroup.add_option('-e', '--region', dest='region', help='Specify CSV output type as county or state.  Defaults to gridded.\nRegion requires -G [grid] command line option.', metavar='region', default='')
    regionGroup.add_option('--srg_file', dest='srgfile', help='Specify path to surrogate file used for getting regions. Defaults to 12km land area.', default=defSrgFile)
    loopGroup.add_option('-r', '--repdays', dest='rep_days', help='Use representative days of specified type: aveday_N, aveday_Y, mwdss_N, mwdss_Y, week_N, week_Y, all\n  Defaults to all', metavar='TYPE', default='')
    loopGroup.add_option('-G', '--grid', dest='grid_name', help='Set the grid name when looping or when writing state/county based reports.', metavar='GRID', default='')
    loopGroup.add_option('-D', '--gsdate', dest='gsdate', help='Set the starting GSDATE when looping.', metavar='YYYYMMDD', default='')
    loopGroup.add_option('-R', '--rundays', dest='run_days', help='Number of days from the starting GSDATE to run for looping.', metavar='1-366', default='')
    loopGroup.add_option('-C', '--case', dest='case', help='Name of case for the input data when looping.', metavar='CASE', default='')
    loopGroup.add_option('-S', '--sector', dest='sector', help='Sector of the input data when looping.', metavar='SECTOR', default='')
    loopGroup.add_option('-P', '--speciation', dest='spec', help='Speciation of the input data for mole->ton conversion and filenames when looping.', metavar='SPEC', default='cmaq_cb6')
    loopGroup.add_option('-I', '--inputpath', dest='inpath', help='Path to the input data.  Used when looping.', metavar='PATH', default='')
    outputGroup.add_option('-o', '--outtype', dest='out_type', help='Output to NCF or CSV.  Default is CSV.', default='CSV')
    outputGroup.add_option('-t', '--tons', action='store_true', dest='tons', help='Convert units from moles/sec to tons/hr.  Defaults to no conversion.', default=False)
    outputGroup.add_option('-F', '--formula', dest='formK', help='Adds existing species into an output species. Format: CALCSPEC1=SPECa+SPECb,CALCSPEC2=SPECc+SPECd,...', default='')
    outputGroup.add_option('-K', '--formula-no-keep', dest='formNK', help='Same as -F, except that all species used in a calculation will not be in output.', default='')
    outputGroup.add_option('-u', '--units', dest='units', help='Override units name.  Default is moles/s or tons/day if -t flag is used.', default='')
    outputGroup.add_option('--all-hours', action='store_true', dest='all_hours', help='Sum up species over all time steps/hours in a file.  Default is to sum first 24 hours.', default=False)
    parser.add_option('--griddesc', dest='griddesc', help='Specify the path to the grid description file', metavar='#', default=defGridDesc)
    parser.add_option_group(regionGroup)
    parser.add_option_group(loopGroup)
    parser.add_option_group(outputGroup)
    return parser.parse_args()

class RunOpts(object):

    def __init__(self):
        self.set_ev()
        options, args = get_opts()
        self.check_valid(options, args)
        self.set_opt_args(options)
        self.set_cmd_args(args)
        self.init_run()

    def set_ev(self):
        '''
        Set the attributes with the environment variables
        '''
        self.evs = {'GRID': 'grid_name', 'GSDATE': 'gsdate', 'CASE': 'case', 'SECTOR': 'sector', 
          'IMD_ROOT': 'inpath', 'SPEC': 'spec', 'GRIDDESC': 'griddesc'}
        for ev, att_name in self.evs.items():
            setattr(self, att_name, check_ev(ev))

    def set_opt_args(self, options):
        '''
        Set the parser options to object attributes
        '''
        int_list = ['run_days','threads']
        lower_list = ['region',]
        upper_list = ['rep_days','informat','out_type']
        for opt, val in options.__dict__.items():
            if type(val) == str:
                val = val.strip()
            if opt in int_list:
                if val != '':
                    val = int(val)
            elif opt in lower_list:
                val = val.lower()
            elif opt in upper_list:
                val = val.upper()
            # Don't override an att that was set by an EV but not set on the command line
            if opt in self.evs and opt == '':
                pass
            else:
                setattr(self, opt, val)

    def set_cmd_args(self, args):
        self.outfile_name = args[0]
        self.run_type = args[1].strip().lower()

    def check_valid(self, options, args):
        '''
        Misc. option validity checks
        '''
        if options.listRuns: 
            listRunTypes() 
        if len(args) != 2: 
            print('Must specify an outfile and a run type.')
            print('Use the -l option to list run types or -h for futher options.')
            exit()
        # Handle species list options
        if options.species_name == '' and not options.all_species: 
            parser.error('No species specified.  Must either specify the -s or -a option.')
        if options.species_name != '' and options.all_species: 
            parser.error('You must only specify either the -s or the -a option.')
        self.species_list = options.species_name.split(',')

    def init_run(self): 
        '''
        Setup other attributes that need additional processing or logic to define
        '''
        self.zip_dict = {} # Dictionary pointing to unzipped input files
        if self.grid_name and self.griddesc:
            self.grid = Grid(self.grid_name, self.griddesc)
        elif self.out_type == 'NCF':
            parser.error('Must specify a grid name and a grid description file when outputting to NCF.')
        else:
            self.grid = ''
        # Set the input file name prefix for inline versus 2D
        if self.inln:
            inprefix = 'inln'
            if not self.grid_name:
                parser.error('Inline to 2D conversion requires setting a grid.  Please specify a grid with -G')
            if not self.stack_file:
                if self.inpath and self.sector and self.grid and self.case:
                    self.stack_file = os.path.join(self.inpath, 'stack_groups_%s_%s_%s.ncf' %(self.sector, 
                      self.grid, self.case))
                else:
                    parser.error('Stack groups file not set.  Please set path using -g.')
            self.stacks = StkGrp(self.stack_file, self.grid).pt_xref
        else:
            inprefix = 'emis'
            self.stacks = ''
        # Load first file to be read to obtain species list
        if len(self.file_name.split(',')) > 1: 
            speciesfile_name = self.file_name.split(',')[0]
        else: 
            speciesfile_name = self.file_name
        # Try to read an individual file from the file list
        if speciesfile_name:
            infile = DataFile(speciesfile_name, self.verbosity, self.informat, self.ptsr, 
              self.zip_dict)
            if not self.gsdate:
                esdate = infile.sdate
                if int(esdate) < 190000:
                    esdate = 2011001
                self.gsdate = conv2greg(esdate)
        # Try to read the first file in a looped case
        else:
            if not self.grid_name or not self.gsdate or not self.case or not self.sector or not self.inpath or not self.spec or not self.run_days:
                parser.error('Must set an input path, case, sector, gsdate, grid, rundays, and speciation OR an input file name (-f).')
            # Handle representative days    
            if self.run_days:
                sdate = dl.InDay(self.gsdate, self.rep_days, self.run_days, smkDatesPath) 
            else:
                sdate = self.gsdate
            if self.sector.lower() == 'mrggrid':
                self.infile_name = os.path.join(self.inpath, 'emis_mole_all_%s_%s_nobeis_%s.ncf' %(sdate, self.grid_name, self.case))
            elif self.sector.lower() == 'mrggrid_withbeis':
                self.infile_name = os.path.join(self.inpath, 'emis_mole_all_%s_%s_withbeis_%s.ncf' %(sdate, self.grid_name, self.case))
            elif self.sector.lower() == 'mrggrid_nobeis':
                self.infile_name = os.path.join(self.inpath, 'emis_mole_all_%s_%s_nobeis_%s.ncf' %(sdate, self.grid_name, self.case))
            else:
               self.infile_name = os.path.join(self.inpath, self.sector, 
                  '%s_mole_%s_%s_%s_%s_%s.ncf' %(inprefix, self.sector, sdate, self.grid_name, 
                  self.spec, self.case))  # v5 directory structure 
            infile = DataFile(self.infile_name, self.verbosity, self.informat, self.ptsr, self.zip_dict)
        # Get species list from open file
        if self.all_species:
            self.species_list = list(species_name for species_name in infile.species_list if species_name != 'TFLAG')
        if self.verbosity and self.layer: 
            print('Running for layer %s' %self.layer)

