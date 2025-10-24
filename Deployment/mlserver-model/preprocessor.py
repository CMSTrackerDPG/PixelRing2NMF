# import external modules
import numpy as np

# import local modules
import dftools as dftools
import omstools as omstools

class PreProcessor(object):
    '''
    Definition and application of preprocessing steps
    '''
    
    def __init__(self,
                 metype
                 ):
        
        # set cropping values for Ring2
        self.anticrop = (slice(68,72), slice(24,32))
            
    def preprocess(self, df, **kwargs):
        '''
        Preprocess the data in a dataframe.
        Input arguments:
        - df: dataframe as read from input files.
        Returns:
        - np array of shape (number of histograms, number of y-bins, number of x-bins)
        '''
        # get histograms
        mes, runs, lumis = dftools.get_mes(df,
                            xbinscolumn='x_bin', ybinscolumn='y_bin',
                            runcolumn='run_number', lumicolumn='ls_number')
        
        # do preprocessing
        return self.preprocess_mes(mes, runs, lumis, **kwargs)
        
    def preprocess_mes(self, mes, runs, lumis, verbose=False):
        # remove empty cross
        if self.anticrop is not None:
            slicey = self.anticrop[0]
            slicex = self.anticrop[1]
            mes = np.delete(mes, slicey, axis=1)
            mes = np.delete(mes, slicex, axis=2)
                
        # return the mes
        return mes
    
    
    def deprocess(self, mes, runs=None, lumis=None):
        '''
        Inverse operation of preprocess, specific for Ring 2 (*4)
        '''
        # insert empty cross
        if self.anticrop is not None:
            mes = np.insert(mes, [int(mes.shape[1]/2)]*4, 0, axis=1)
            mes = np.insert(mes, [int(mes.shape[2]/2)]*8, 0, axis=2)
            
        return mes
