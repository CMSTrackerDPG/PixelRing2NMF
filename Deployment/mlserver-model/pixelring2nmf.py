# Model definition

# note: inside the container, only the files in the mlserver-model directory are visible.
#       importing local modules from outside this directory is not trivial
#       (although allegedly possible by making everything a package, but I did not test that yet),
#       and the simplest (though far from optimal) solution might be to duplicate all local dependencies
#       in this local model definition...


# import external modules
import sys
import numpy as np

# import local modules
import dftools as dftools
import functions as functions
import bad_ROC as bad_ROC
from nmf2d import NMF2D
from preprocessor import PreProcessor

class PixelRing2NMF(object):
    # implementation of NMF model (including all pre- and post-processing steps)
    # for the pixel cluster occupancy Ring 2 monitoring element.
    
    def __init__(self,
                 nmfs,
                 thresholds = None,
                 ):
        '''
        Initializer.
        Input arguments:
        - nmfs: dictionary of the following form: {monitoring element name: NMF model, ...}
        - local_norms: dictionary of the following form: {monitoring element name: local norm (2D np array), ...}
        - loss_masks: dictionary of the following form: {monitoring element name: loss mask (2D np array), ...}
        '''
        
        # get monitoring element names for later use
        self.menames = list(nmfs.keys())[:]
        
        self.nmfs = {}
        for mename, nmf in nmfs.items():
            if not isinstance(nmf, NMF2D):
                msg = f'WARNING in PixelNMF.__init__: received object of type {type(nmf)},'
                msg += ' while an NMF2D model was expected; things might break further downstream.'
                print(msg)
            self.nmfs[mename] = nmf
        
        # check NMF models
        # note: one model per monitoring element
        if not isinstance(nmf, NMF2D):
            msg = f'WARNING in PixelRing2NMF.__init__: received object of type {type(nmf)},'
            msg += ' while an NMF2D model was expected; things might break further downstream.'
            print(msg)
        
        # make preprocessors
        self.preprocessors = {}
        for mename in self.menames:
            self.preprocessors[mename] = PreProcessor(mename)
        
        # Define Thresholds
        # loss > 1e5
        # fraction > 0.4
        self.thresholds = thresholds
        if self.thresholds is None:
            self.thresholds = {"loss_threshold": 1e5, "ROC_fraction": 40}
    
    def preprocess(self, X, verbose=False):
        '''
        Do preprocessing (from raw MEs to input for the NMF model).
        Input arguments:
        - X: dictionary of the following form {monitoring element name: raw data (2D np array), ...}
        '''
        mes_preprocessed = {}
        if verbose: print('[INFO]: preprocessing...')
        for mename in self.menames:
            mes_preprocessed[mename] = self.preprocessors[mename].preprocess_mes(X[mename], None, None)
            
        return mes_preprocessed
    
    def deprocess(self, X, verbose=False):
        mes_deprocessed = {}
        if verbose: print('[INFO]: deprocessing...')
        for mename in self.menames:
            mes_deprocessed[mename] = self.preprocessors[mename].deprocess(X[mename], None, None)

        return mes_deprocessed

            
    def infer(self, X, verbose=False):
        '''
        Run NMF inference/reconstruction.
        Input arguments:
        - X: dictionary of the following form {monitoring element name: preprocessed data (2D np array), ...}
        '''
        if verbose: print('[INFO]: running inference...')
        mes_reco = {}
        for mename in self.menames:
            X_input = np.copy(X[mename])
            X_input = np.nan_to_num(X_input, nan=0)
            mes_reco[mename] = self.nmfs[mename].predict(X_input)
        return mes_reco      
    
    def loss(self, X_input, X_reco, do_thresholding=True, verbose=False):
        '''
        Do loss calculation.
        Input arguments:
        - X_input and X_reco: dictionary of the following form {monitoring element name: data (2D np array), ...}
          with input data (preprocessed) and NMF reconstruction respectively.
        '''
        losses = {}
        if verbose: print('[INFO]: calculating losses...')
        for mename in self.menames:
            losses[mename] = np.square(X_input[mename] - X_reco[mename])
        return losses
        
    def flag(self, X_loss, verbose=False):
        '''
        Do final flagging of combined loss map.
        Input arguments:
        - X_loss: combined loss (2D np array)
        '''
        
        flags = bad_ROC.search_for_anomalies(X_loss, self.thresholds)
        return flags
    
    def get_filter_mask(self, X_input, oms_data=None, verbose=False):
        '''
        Apply filters.
        Note: HLT rate filter not yet implemented.
        Note: filters hard-coded in this function for now, maybe generalize later.
        Input arguments:
        - X_input: dictionary of the following form {monitoring element name: data (3D np array), ...} with input data.
        - oms_data: dictionary of the following form {OMS attribute name: data (1D np array), ...} with OMS info.
                    note: for now, the lumisections in oms_data are assumed to exactly match those in X_input,
                          maybe generalize and make more robust later.
        '''
        
        # initializations
        if verbose: print('[INFO]: applying filter...')
        menames = sorted(list(X_input.keys()))
        mask = np.ones(len(X_input[menames[0]])).astype(bool)
        
        # define run numbers and lumisection numbers
        run_numbers = np.zeros(len(mask))
        ls_numbers = np.zeros(len(mask))
        if oms_data is not None:
            run_numbers = oms_data['run_number']
            ls_numbers = oms_data['lumisection_number']

        # define OMS filters
        oms_filters = None
        if oms_data is not None:
            oms_filters = [
              ["beams_stable"],
              ["cms_active"],
              ["bpix_ready"],
              ["fpix_ready"],
              ["tibtid_ready"],
              ["tob_ready"],
              ["tecp_ready"],
              ["tecm_ready"],
              #["pileup", '>', 25],
              #["hlt_zerobias_rate", '>', 5]
            ]
            for oms_filter in oms_filters:
                key = oms_filter[0]
                if key not in oms_data.keys():
                    msg = f'Provided OMS data does not contain the expected key {key}'
                    raise Exception(msg)

        # apply the filter
        mask, _ = dftools.filter_lumisections(run_numbers, ls_numbers,
                    oms_info = oms_data, oms_filters = oms_filters,
                  )

        # total mask printouts
        if verbose:
            ntot = len(mask)
            npass = np.sum(mask.astype(int))
            print(f'[INFO]: total mask: {npass} / {ntot} passing lumisections.')
            
        # return mask
        return mask
        
    def predict(self, X, verbose=False):
        '''
        Run full chain on incoming data X
        '''
        if verbose:
            print('[INFO]: Running PixelRing2NMF.predict on the following data:')
            for key, val in X.items():
                print(f'  - {key}: {val.shape}')
            
        # split ME and OMS data
        menames = ['Ring2']
        X_input = {key: val for key, val in X.items() if key in menames}
        oms_input = {key: val for key, val in X.items() if key not in menames}
        oms_input = {key.split('__')[-1]: val for key, val in oms_input.items()}
        if verbose:
            print('Found following OMS keys for filtering:')
            print(oms_input.keys())
        if len(oms_input.keys())==0:
            oms_input = None

        # do preprocessing, inference, and loss calculation
        mes_preprocessed = self.preprocess(X_input, verbose=verbose)
        mes_reco = self.infer(mes_preprocessed, verbose=verbose)
        losses = self.loss(mes_preprocessed, mes_reco, do_thresholding=True, verbose=verbose)
        losses_with_cross = self.deprocess(losses, verbose=verbose)
        flags = self.flag(losses_with_cross, verbose=verbose)

        # printouts for testing and debugging
        nflags = np.sum(flags.astype(int))
        msg = '[INFO]: Flagging results (before filtering):'
        msg += f' flagged {nflags} out of {len(flags)} lumisections.'
        print(msg)

        # apply mask
        mask = self.get_filter_mask(X_input, oms_data=oms_input, verbose=verbose)
        flags[~mask] = False

        # printouts for testing and debugging
        nselected = np.sum(mask.astype(int))
        msg = f'[INFO]: Filtering: selected {nselected} out of {len(flags)} lumisections.'
        print(msg)
        nflags = np.sum(flags.astype(int))
        msg = '[INFO]: Flagging results (after filtering):'
        msg += f' flagged {nflags} out of {len(mask)} lumisections.'
        print(msg)
        sys.stdout.flush()
        sys.stderr.flush()
        
        # return final result
        return flags
