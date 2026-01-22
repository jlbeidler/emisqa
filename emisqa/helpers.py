import os
from datetime import timedelta, date, datetime
from emisqa.chem_mechs import *

# Helper procedures    
def check_ev(ev_name):
    """
    Checks if an environment variable is set.
    """
    try: 
        var = os.environ[ev_name]
    except KeyError: 
        return '' 
    else: 
        return var

def parse_float(x):
    """
    Returns a floating point with the correct number of trailing zeros based on the .Dx
    """
    from math import pow
    from numpy import float64
    if 'D' in x:    
        num = float(x.strip().split('D')[0])
        exp = int(x.strip().split('D')[1])
        return float64(num * pow(10, exp))
    else:
        return float64(x)

def conv2jul(gsdate):
    """
    Returns Julian date from Gregorian date.
    """
    gdate = datetime.strptime(str(gsdate), '%Y%m%d')
    return int(datetime.strftime(gdate, '%Y%j'))

def conv2greg(jul_date):
    """
    Returns Gregorian date from a Julian date.
    """
    jdate = datetime.strptime(str(jul_date), '%Y%j')
    return datetime.strftime(jdate, '%Y%m%d')

def moles2tons(val, species_name, in_format, mech = 'cmaq_cb05'):
    """
    Converts a value or array of values from moles/s to tons/hr
    """
    mechDct = molecDct[mech]

    if species_name in mechDct: 
        factor = mechDct[species_name]
    else: 
        factor = 1

    val = val * factor   # Convert moles per second to grams per second

    if in_format != 'UAM':
        val = val * 3600   # Convert tons per second to tons per hour

    val = val * (0.00000110231131)  # Convert grams per hour to tons per hour 

    return val  

def data_blocks(infile, size=1024):
    """
    Reads in binary files by blocks
    """
    while True:
        block = infile.read(size)
        if len(block) == 0:
            break
        yield block

def clean_temp(zip_dict):
    """
    Cleans up the temporary zip output files at the end of a run.
    """
    if len(zip_dict) == 0: 
        return
    for name in zip_dict:
        os.remove(zip_dict[name])


