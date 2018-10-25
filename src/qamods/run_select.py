from qamods.runtypes import *
import multiprocessing

def runQA(opts):
    # Select run type and run the script.
    # Run types dictionary contains x-reference from command line run type name to run type function name 
    run_types = {'pe': pe, 'add': add_files, 'dv': dump_dv, 'sum': sumdv, 'avg': avgdv, 
      'domain': single_domain, 'mm': mm_domain, 'rd': raw_diff, 'dump': raw_dump, 'hd': hour_dump, 
      'yd': hourly_domain, 'sumhour': sumhour}
    if opts.run_type not in run_types: 
        raise ValueError('Specified run type not available.  Please refer to the list of run types using the -l argument.')
    pool = multiprocessing.Pool(opts.threads)
    workers = [pool.apply_async(run_types[opts.run_type].get_spec, (species_name, opts)) for species_name in opts.species_list] 
    out_dict = dict([worker.get() for worker in workers])
    pool.close()
    pool.join()
    # Convert to tons by species if conversion is turned on
    if opts.tons: 
        for speciesName in list(out_dict.keys()):
            out_dict[speciesName].moles2tons(opts.informat, opts.spec)
    return out_dict

