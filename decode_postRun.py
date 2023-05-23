"""
Decode raw data (bitstreams) after data-taking, save decoded information in CSV format identical to when running beam_test.py with option -c

Author: Amanda Steinhebel
amanda.l.steinhebel@nasa.gov
"""

from astropix import astropix3
import glob
import binascii
import pandas as pd
import numpy as np
import logging
import argparse
import re
import time

from modules.setup_logger import logger

# This is the dataframe which is written to the csv if the decoding fails
decode_fail_frame = pd.DataFrame({
                'readout': np.nan,
                'Chip ID': np.nan,
                'payload': np.nan,
                'location': np.nan,
                'isCol': np.nan,
                'timestamp': np.nan,
                'tot_msb': np.nan,
                'tot_lsb': np.nan,
                'tot_total': np.nan,
                'tot_us': np.nan,
                'hittime': np.nan
                }, index=[0]
)


#Initialize
def main(args):
        
    #Allow only -f or -d to be evoked - not both
    if args.fileInput and args.dirInput:
        logger.error("Input a single file with -f OR a single directory with -d... not both! Try running again")
        exit()

    #Define boolean for args.fileInput
    f_in = True if args.fileInput is not None else False

    #Create objet
    astro = astropix3(offline=True)

    #Define output file path
    if args.outDir is not None:
        outpath = args.outDir
    elif f_in:
        try: #Mac path
            dirInd = args.fileInput.rindex('/')
        except ValueError: #Windows path
            dirInd = args.fileInput.rindex('\\')
        outpath = args.fileInput[:dirInd+1] #add 1 to keep final delimiter in path
    elif args.dirInput is not None:
        outpath = args.dirInput
    
    #Symmetrize structure
    inputFiles = [args.fileInput] if f_in else glob.glob(f'{args.dirInput}*.log')

    #Run over all input files
    for infile in inputFiles:

        #Define output file name
        csvname = re.split(r'\\|/',infile)[-1][:-4] #split Mac or OS path; identify file name and eliminate '.log'
        csvpath = outpath + csvname + '_offline.csv'

        #Setup CSV structure
        csvframe =pd.DataFrame(columns = [
                'readout',
                'Chip ID',
                'payload',
                'location',
                'isCol',
                'timestamp',
                'tot_msb',
                'tot_lsb',
                'tot_total',
                'tot_us',
                'hittime'
        ])

        #Import data file            
        f=np.loadtxt(infile, skiprows=6, dtype=str)

        #isolate only bitstream without b'...' structure 
        strings = [a[2:-1] for a in f[:,1]]
        #print(strings)

        i = 0
        errors=0

        for s in strings:
            #convert hex to binary and decode
            rawdata = list(binascii.unhexlify(s))
            #print(rawdata)
            try:
                hits = astro.decode_readout(rawdata, i, printer = args.printDecode)
                #print(hits)
                hits.hittime = time.time()
            except IndexError:
                errors += 1
                logger.warning(f"Decoding failed. Failure {errors} on readout {i}")
                hits = decode_fail_frame
                #hits.rawdata = i
                hits['hittime']=np.nan
            finally:
                i += 1
                #Overwrite hittime - computed during decoding
                #Populate csv
                csvframe = pd.concat([csvframe, hits])
                #csvframe.readout = csvframe.readout.astype(int)
        #Save csv
        logger.info(f"Saving to {csvpath}")
        csvframe.to_csv(csvpath)
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Post-run decoding')
    parser.add_argument('-f', '--fileInput', default=None, required=True,
                    help='Input data file to decode')

    parser.add_argument('-d', '--dirInput', default=None, required=False,
                    help='Input directory of data files to decode')

    parser.add_argument('-o', '--outDir', default='/home/labadmin/AstropPix/BeamTest0523/BeamData/chip_v3_APS3-W2-S03/', required=False,
                    help='Output Directory for all decoded datafiles. Defaults to directory raw data is saved in')

    parser.add_argument('-L', '--loglevel', type=str, choices = ['D', 'I', 'E', 'W', 'C'], action="store", default='I',
                    help='Set loglevel used. Options: D - debug, I - info, E - error, W - warning, C - critical. DEFAULT: D')

    parser.add_argument('-p', '--printDecode', action='store_true', default=True, required=False,
                    help='Print decoded info into terminal. Default: False')

    #python3.9 decode_postRun.py -f "../BeamTest0223/BeamData/Chip_230103/run17_protons120_20230224-090711.log" -o "../BeamTest0223/BeamData/Chip_230103/" -L D -p

    parser.add_argument
    args = parser.parse_args()

    # Sets the loglevel
    ll = args.loglevel
    if ll == 'D':
        loglevel = logging.DEBUG
    elif ll == 'I':
        loglevel = logging.INFO
    elif ll == 'E':
        loglevel = logging.ERROR
    elif ll == 'W':
        loglevel = logging.WARNING
    elif ll == 'C':
        loglevel = logging.CRITICAL
    
    # Logging - print to terminal only
    formatter = logging.Formatter('%(asctime)s:%(msecs)d.%(name)s.%(levelname)s:%(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)

    logging.getLogger().addHandler(sh) 
    logging.getLogger().setLevel(loglevel)

    logger = logging.getLogger(__name__)

    
    main(args)
