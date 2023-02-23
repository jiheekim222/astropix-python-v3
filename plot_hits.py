"""
02/2023 Jihee Kim added making plots from csv file of beam measurements
"""
import argparse
import csv
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

def main(args):
    # Read csv
    df = pd.read_csv(args.beamdata)
    
    # Skip rows with NAN
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.dropna()

    # Get total number of readouts/events per run
    max_n_readouts = df['readout'].iloc[-1]
   
    # List for hit pixels
    pair = []
    
    # Loop over readouts/events
    for ievt in range(0, max_n_readouts, 1):
        # Collect one event
        dff = df.loc[(df['readout'] == ievt) & (df['payload'] == 4)]
        
        # List column info of pixel within one event
        dffcol = dff.loc[dff['isCol'] == True]
        
        # List row info of pixel within one event
        dffrow = dff.loc[dff['isCol'] == False]
        
        # time difference in time over threshold (tot) in us to define a pixel
        tot_time_limit = 0.3
        # Loop over col and row info to find a pair to define a pixel
        for indc in dffcol.index:
            for indr in dffrow.index:
                if (dffcol['timestamp'][indc] == dffrow['timestamp'][indr]) & (abs(dffcol['tot_us'][indc] - dffrow['tot_us'][indr]) < tot_time_limit):
                    # Record hit pixels per event
                    pair.append([dffcol['location'][indc], dffrow['location'][indr], dffcol['timestamp'][indc], dffrow['timestamp'][indr], dffcol['tot_us'][indc], dffrow['tot_us'][indr]])

    # Hit pixel information for all events
    dffpair = pd.DataFrame(pair, columns=['col', 'row', 'timestamp_col', 'timestamp_row', 'tot_us_col', 'tot_us_row'])
    # For heatmap plot, it needs col, row, and hits 
    dfpair = dffpair[['col','row']].copy()
    dfpairc = dfpair[['col','row']].value_counts().reset_index(name='hits')
    print(dfpairc.to_string())

    # Generate Plot
    ax = plt.hist2d(x=dfpairc['col'],y=dfpairc['row'],bins=35,range=[[-0.5,34.5],[-0.5,34.5]], weights=dfpairc['hits'],cmap='viridis')
    bar = plt.colorbar()
    plt.xlabel('col', fontsize=15)
    plt.ylabel('row', fontsize=15)
    bar.set_label('hits', fontsize=15)
    plt.title(f"{args.name} Run {args.runnum}")
    plt.savefig(f"{args.outdir}/tot_hit_plot_run{args.runnum}.png")

    # END OF PROGRAM
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Astropix Driver Code')
    parser.add_argument('-n', '--name', default='', required=False,
                    help='Option to give additional name to output files upon running')

    parser.add_argument('-o', '--outdir', default='.', required=False,
                    help='Output Directory for all datafiles')

    parser.add_argument('-df', '--beamdata', action='store', required=False, type=str, default = 'example_beam_data.csv',
                    help = 'filepath beam data file to be plotted.')

    parser.add_argument('-rn', '--runnum', type=int, action='store', default=None,
                    help = 'run number')
    
    parser.add_argument
    args = parser.parse_args()

    main(args)
