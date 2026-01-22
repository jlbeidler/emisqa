import numpy as np
import scipy.sparse
import pandas as pd

class Surrogate():
    '''
    Defines a degridding surrogate table for each FIPS on a sparse matrix
    self.arr = [fips, flattened grid matrix] = cell to county factor
    self.fips = list of fips in axis = 0 array order
    '''
    
    def __init__(self, grid):
        self.arr = False
        self.fips = []
        self.grid = grid

    def _set_srg_grid(self, l):
        '''
        Calculate and set the grid cell offsets between the surrogate and model grid
        '''
        xorig = float(l[2])
        yorig = float(l[3])
        self.col_offset = abs(int(old_div((xorig - self.grid.XORIG), self.grid.XCELL)))
        self.row_offset = abs(int(old_div((yorig - self.grid.YORIG), self.grid.YCELL)))
        self.col_range = range(1 + self.col_offset, self.grid.NCOLS + 1 + self.col_offset)
        self.row_range = range(1 + self.row_offset, self.grid.NROWS + 1 + self.row_offset)

    def load_surrogate(self, region, srg_file):
        '''
        Load the surrogate into a dictionary of FIPS with a value of fractions on the grid
        '''
        cell_area = self.grid.XCELL * self.grid.YCELL
        with open(srg_file) as infile:
            for line in infile:
                line = [cell.strip() for cell in line.split('\t') if cell and cell != '!']
                if line[0].startswith('#') or line[0].strip() == '': 
                    if line[0].strip() == '#GRID':
                        self._set_srg_grid(line)
                else:
                    break
        cols = ['code','fips','col','row','fac','a','cellarea','ctyarea']
        usecols = ['fips','col','row','cellarea','ctyarea']
        dtype = {'fips': str, 'col': str, 'row': str}
        df = pd.read_csv(srg_file, names=cols, usecols=usecols, dtype=dtype, sep='\t',
          skipinitialspace=True, comment='#', index_col=False)
        if region == 'state':
            df['fips'] = df['fips'].str.strip().str[:2]
        df['col'] = df['col'].str.strip().astype(int) - self.col_offset - 1
        df['row'] = df['row'].str.strip().astype(int) - self.row_offset - 1
        idx = (df['col'].isin(range(self.grid.NCOLS))) & (df['row'].isin(range(self.grid.NROWS)))
        df = df[idx].copy()
        if region == 'countyavg':
            df['frac'] = df['cellarea'] / df['ctyarea']
        else:
            df['frac'] = df['cellarea'] / cell_area 
        return df[['fips','row','col','frac']].copy()

    def calc_fracs(self, region, srg_file):
        """
        Parses in the county to grid conversion ratios.
        """
        srg = self.load_surrogate(region, srg_file)
        self.fips = sorted(list(srg['fips'].drop_duplicates()))
        self.arr = np.zeros([len(self.fips), self.grid.NROWS, self.grid.NCOLS], 'f')
        # Clean this up, lotta looping
        #idx = pd.MultiIndex.from_product((range(self.grid.NROWS), range(self.grid.NCOLS)))
        # Set index...reindex...etc.
        #  fipsrg = srg[srg['fips'] == fips]
        #  Or self.arr[n,:] = coo_matrix((fipssrg.frac, (fipssrg.row, fipssrg.col)), shape=(grid.NROWS, grid.NCOLS)).toarray()
        for n, fips in enumerate(self.fips):
            for row in srg[srg['fips'] == fips].iterrows():
                self.arr[n,row[1]['row'],row[1]['col']] = row[1]['frac']
        self.arr = scipy.sparse.bsr_matrix(self.arr.reshape(len(self.fips), self.grid.NROWS*self.grid.NCOLS))


