"""
02/2023 Jihee Kim added making plots from csv file of beam measurements
"""
import argparse
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import glob

def main(args):
   
    # Path to beamdata location
    path = args.datadir
    # Collect a list of multiple beamdata files
    filename_list = [f"{path}/run{runnum}_*.csv" for runnum in args.runnolist]
    # Read multiple beamdata csv files
    all_files = []
    for fname in filename_list:
        nfile = glob.glob(fname)
        all_files += nfile
    df = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)

    # Skip rows with NAN
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.dropna()

    # Changed float to int for readout col
    df['readout'] = df['readout'].astype('Int64')
    # Get total number of readouts/events per run
    max_n_readouts = df['readout'].iloc[-1]
   
    # List for hit pixels
    pair = []
   
    # Loop over readouts/events
    for ievt in range(0, max_n_readouts, 1):
        # Collect one event
        if args.exclusively:
            dff = df. loc[(df['readout'] == ievt)] 
        else:
            dff = df.loc[(df['readout'] == ievt) & (df['payload'] == 4)]
        
        n_no_good_decoding = 0
        for payload in dff['payload']:
            if payload != 4:
               n_no_good_decoding += 1 
        
        if n_no_good_decoding != 0:
            break
        else:
            # List column info of pixel within one event
            dffcol = dff.loc[dff['isCol'] == True]
        
            # List row info of pixel within one event
            dffrow = dff.loc[dff['isCol'] == False]
        
            # time difference in time over threshold (tot) in us to define a pixel
            tot_time_limit = 1.0 # before more exclusive cut on 0.3
            # Loop over col and row info to find a pair to define a pixel
            for indc in dffcol.index:
                for indr in dffrow.index:
                    # Before more exclusive cut on timestamp like exact same
                    if (abs(dffcol['timestamp'][indc] - dffrow['timestamp'][indr]) < 1.1) & (abs(dffcol['tot_us'][indc] - dffrow['tot_us'][indr]) < tot_time_limit):
                        # Record hit pixels per event
                        pair.append([dffcol['location'][indc], dffrow['location'][indr], dffcol['timestamp'][indc], dffrow['timestamp'][indr], dffcol['tot_us'][indc], dffrow['tot_us'][indr]])

    # Hit pixel information for all events
    dffpair = pd.DataFrame(pair, columns=['col', 'row', 'timestamp_col', 'timestamp_row', 'tot_us_col', 'tot_us_row'])
    # For heatmap plot, it needs col, row, and hits 
    dfpair = dffpair[['col','row']].copy()
    dfpairc = dfpair[['col','row']].value_counts().reset_index(name='hits')
    print(dfpairc.to_string())

    # Print run number(s)
    runnum = '-'.join(args.runnolist)
    # Generate Plot
    ax = plt.hist2d(x=dfpairc['col'],y=dfpairc['row'],bins=35,range=[[-0.5,34.5],[-0.5,34.5]], weights=dfpairc['hits'], cmap='YlOrRd',cmin=1.0)
    bar = plt.colorbar()
    plt.xlabel('col', fontsize=15)
    plt.ylabel('row', fontsize=15)
    bar.set_label('hits', fontsize=15)
    plt.title(f"{args.name} Run {runnum}")
    plt.savefig(f"{args.outdir}/tot_hit_plot_run_{runnum}.png")
   
    dfnoise = pd.read_csv(args.noisedir)
    print(dfnoise)
    dfnoise['Masking'] = 0
    print(dfnoise)
    dfnoise['Masking'] = np.where(dfnoise['Count'] > 5, 1, dfnoise['Masking']) 
    print(dfnoise.to_string())

    ax2 = plt.hist2d(x=dfnoise['Col'],y=dfnoise['Row'],bins=35,range=[[-0.5,34.5],[-0.5,34.5]], weights=dfnoise['Masking'], cmap='Greys')
    bar2 = plt.colorbar()
    plt.xlabel('col', fontsize=15)
    plt.ylabel('row', fontsize=15)
    bar2.set_label('masking', fontsize=15)
    plt.title(f"{args.name} masking")
    plt.savefig(f"{args.outdir}/{args.name}_masking.png")

    # END OF PROGRAM
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Astropix Driver Code')
    parser.add_argument('-n', '--name', default='', required=False,
                    help='Option to give additional name to output files upon running')

    parser.add_argument('-o', '--outdir', default='./', required=False,
                    help='Output Directory for all datafiles')

    parser.add_argument('-d', '--datadir', action='store', required=True, type=str, default = 'path_to_data',
                    help = 'filepath beam data file to be plotted.')
    
    parser.add_argument('-s', '--noisedir', action='store', required=True, type=str, default = 'path_to_noise_data',
                    help = 'filepath noise scan file to mask pixel for plotting purpose.')

    parser.add_argument('-l','--runnolist', nargs='+', required=True,
                    help = 'List run number(s) you would like to see')
    
    parser.add_argument('--exclusively', default=False, action='store_true', 
                    help='Throw entire readout data if some has bad decoding')

    parser.add_argument
    args = parser.parse_args()

    main(args)
