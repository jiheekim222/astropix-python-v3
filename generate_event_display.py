"""
02/2023 Jihee Kim added number of events from csv file of beam measurements
"""
import argparse
import csv
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
import glob
import os
plt.style.use('classic')

def main(args):
   
    ##### Find and Combine all data files #####################################
    # Path to beam data location
    path = args.datadir
    # Collect a list of multiple beamdata files
    filename_list = [f"{path}/run{runnum}_*.csv" for runnum in args.runnolist]
    # List multiple beamdata csv files
    all_files = []
    for fname in filename_list:
        nfile = glob.glob(fname)
        all_files += nfile
    ###########################################################################

    ##### Loop over data files and Find hit pixels #######################################################
    # List for hit pixels
    pair = [] 
    # How many events are remained in one dataset
    tot_n_nans = 0
    tot_n_evts = 0
    n_evt_excluded = 0
    n_evt_used = 0
    # Loop over file
    for f in all_files:
        # Read csv file
        df = pd.read_csv(f)
        print(f"Reading in {f}...")
     
        # Count per run
        # Total number of rows
        n_all_rows = df.shape[0]
        # Non-NaN rows
        n_non_nan_rows = df['readout'].count() 
        # NaN events
        n_nan_evts = n_all_rows - n_non_nan_rows
        # Skip rows with NAN
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.dropna()
        # Change float to int for readout col
        df['readout'] = df['readout'].astype('Int64')
        # Get last number of readouts/events per run
        max_readout_n = df['readout'].iloc[-1]
        
        # Count for summary if multiple runs are read in
        ni = 0
        for ievt in range(0, max_readout_n+1, 1):
            dff = df.loc[(df['readout'] == ievt)] 
            if dff.empty:
                continue
            else:
                ni += 1
        n_evts = ni + n_nan_evts
        tot_n_evts += n_evts
        tot_n_nans += n_nan_evts

        # Loop over readouts/events
        for ievt in range(0, max_readout_n+1, 1):
            # Collect one event
            if args.exclusively:
                dff = df. loc[(df['readout'] == ievt)] 
            else:
                dff = df.loc[(df['readout'] == ievt) & (df['payload'] == 4)]
            # Check if it's empty
            if dff.empty:
                continue

            # Check how many bad decoding lines within one event 
            n_no_good_decoding = 0
            for payload in dff['payload']:
                if payload != 4:
                    n_no_good_decoding += 1 
            if n_no_good_decoding != 0:
                n_evt_excluded += 1
                pass
            # Match col and row to find hit pixel
            else:
                n_evt_used += 1
                # List column info of pixel within one event
                dffcol = dff.loc[dff['isCol'] == True]
                # List row info of pixel within one event
                dffrow = dff.loc[dff['isCol'] == False]
                # Matching conditions: timestamp and time-over-threshold (ToT)
                timestamp_diff = args.timestampdiff
                tot_time_limit = args.totdiff
                # Loop over col and row info to find a pair to define a pixel
                for indc in dffcol.index:
                    for indr in dffrow.index:
                        if ((abs(dffcol['timestamp'][indc] - dffrow['timestamp'][indr]) < timestamp_diff) & 
                        (abs(dffcol['tot_us'][indc] - dffrow['tot_us'][indr]) < tot_time_limit)):
                            # Record hit pixels per event
                            pair.append([dffcol['location'][indc], dffrow['location'][indr], 
                                         dffcol['timestamp'][indc], dffrow['timestamp'][indr], 
                                         dffcol['tot_us'][indc], dffrow['tot_us'][indr],
                                        (dffcol['tot_us'][indc] + dffrow['tot_us'][indr])/2])
        print("... Matching is done!")
    ######################################################################################################

    ##### Summary of how many events being used ###################################################
    nevents = '%.2f' % ((n_evt_used/(tot_n_evts)) * 100.)
    nnanevents = '%.2f' % ((tot_n_nans/(tot_n_evts)) * 100.)
    n_empty = tot_n_evts - n_evt_used - tot_n_nans
    nemptyevents = '%.2f' % ((n_empty/(tot_n_evts)) * 100.)
    print("Summary:")
    print(f"{tot_n_nans} of {tot_n_evts} events were found as NaN...")
    print(f"{n_empty} of {tot_n_evts} events were found as empty...")
    print(f"{n_evt_used} of {tot_n_evts} events were processed...")
    if args.exclusively:
        print(f"{n_evt_excluded} of {tot_n_evts} events were excluded because of bad payload...")
        print(f"{nevents}[%] are used in exclusively mode...")
        print(f"{nnanevents}[%] are trashed...")
        print(f"{nemptyevents}[%] are emptied...")
    else:
        print(f"{nevents}[%] are used...")
        print(f"{nnanevents}[%] are trashed...")
        print(f"{nemptyevents}[%] are emptied...")
    ###############################################################################################

    ##### Create hit pixel dataframes #######################################################
    # Hit pixel information for all events
    dffpair = pd.DataFrame(pair, columns=['col', 'row', 
                                          'timestamp_col', 'timestamp_row', 
                                          'tot_us_col', 'tot_us_row', 'avg_tot_us'])
    # Create dataframe for number of hits 
    dfpair = dffpair[['col','row']].copy()
    dfpairc = dfpair[['col','row']].value_counts().reset_index(name='hits')
    # How many hits are collected and shown in a plot
    nhits = dfpairc['hits'].sum()
    
    # Create dataframe for number of hits per 5 by 5 pixels grid
    i = 0
    n_group = 5
    center = round(n_group/2)
    npixels = 0
    paircsmooth = []
    while i < 35:
        j = 0
        while j < 35:
            df_or = dfpairc[((dfpairc['col'] >= i) & (dfpairc['col'] < i+5)) & 
                            ((dfpairc['row'] >= j) & (dfpairc['row'] < j+5))]
            paircsmooth.append([i+center, j+center, df_or['hits'].sum()/df_or.shape[0]])
            npixels += df_or.shape[0]
            j += n_group
        i += n_group
    dfpaircsmooth =pd.DataFrame(paircsmooth, columns=['col', 'row', 'hits'])
    npixel = '%.2f' % ((npixels/1225) * 100.)

    # Create masking map for pixels
    # Path to noise scan data location
    path = args.noisedir
    # Find noise scan data and Read
    filename = args.noisedir + '/noise_scan_summary_' + args.name +'*.csv'
    file = glob.glob(filename)

    for f in file:
        dfnoise = pd.read_csv(f)
    dfnoise['Masking'] = 0
    dfnoise['Masking'] = np.where(dfnoise['Count'] > args.noisethreshold, 1, dfnoise['Masking']) 
    # Calculate how many pixels are good
    npixels = '%.2f' % ((dfnoise['Masking'].value_counts()[0]/1225.) * 100.)

    # Create dataframe for normalized time-over-threshold per pixel
    i = 0
    pixel = []
    while i < 35:
        j = 0
        while j < 35:
            df_and = dffpair[((dffpair['col'] == i) & (dffpair['row'] == j))]    
            if df_and.empty:
                j += 1
                continue
            else:
                pixel.append([i, j, 
                              df_and['avg_tot_us'].sum()/df_and.shape[0]])
                j += 1
        i += 1
    dfpixel = pd.DataFrame(pixel, columns=['col', 'row', 'norm_sum_avg_tot_us'])
    # Create dataframe for normalized time-over-threshold per 5 by 5 pixels grid
    i = 0
    n_group = 5
    center = round(n_group/2)
    pixelsmooth = []
    while i < 35:
        j = 0
        while j < 35:
            df_or = dfpixel[((dfpixel['col'] >= i) & (dfpixel['col'] < i+5)) & 
                            ((dfpixel['row'] >= j) & (dfpixel['row'] < j+5))]
            pixelsmooth.append([i+center, j+center, 
                                df_or['norm_sum_avg_tot_us'].sum()/df_or.shape[0]])
            j += n_group
        i += n_group
    
    dfpixelsmooth = pd.DataFrame(pixelsmooth, columns=['col', 'row', 'norm_sum_avg_tot_us'])
    #########################################################################################

    # Print run number(s)
    runnum = '-'.join(args.runnolist)
    
    # Generate Plot - Pixel hits
    #fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(20, 8))
    row = 2
    col = 3
    fig, ax = plt.subplots(row, col, figsize=(40, 20))
    for irow in range(0, row):
        for icol in range(0, col):
            for axis in ['top','bottom','left','right']:
                ax[irow, icol].spines[axis].set_linewidth(1.5)

    p1 = ax[0, 0].hist2d(x=dfpairc['col'], y=dfpairc['row'], bins=35, range=[[-0.5,34.5],[-0.5,34.5]], weights=dfpairc['hits'], cmap='Reds', cmin=1.0, norm=matplotlib.colors.LogNorm())
    fig.colorbar(p1[3], ax=ax[0, 0]).set_label(label='Hits', weight='bold', size=18)
    ax[0, 0].set_xlabel('Col', fontweight = 'bold', fontsize=18)
    ax[0, 0].set_ylabel('Row', fontweight = 'bold', fontsize=18)
    ax[0, 0].xaxis.set_tick_params(labelsize = 18)
    ax[0, 0].yaxis.set_tick_params(labelsize = 18)

    p2 = ax[0, 1].hist2d(x=dfnoise['Col'],y=dfnoise['Row'],bins=35,range=[[-0.5,34.5],[-0.5,34.5]], weights=dfnoise['Masking'], cmap='Greys')
    fig.colorbar(p2[3], ax=ax[0, 1]).set_label(label='Masking', weight='bold', size=18)
    ax[0, 1].set_xlabel('Col', fontweight = 'bold', fontsize=18)
    ax[0, 1].set_ylabel('Row', fontweight = 'bold', fontsize=18)
    ax[0, 1].xaxis.set_tick_params(labelsize = 18)
    ax[0, 1].yaxis.set_tick_params(labelsize = 18)

    p6 = ax[0, 2].hist2d(x=dfpairc['col'], y=dfpairc['row'], bins=35, range=[[-0.5,34.5],[-0.5,34.5]], weights=dfpairc['hits'], cmap='Reds', cmin=1.0, norm=matplotlib.colors.LogNorm(), alpha=1.0)
    ax[0, 2].hist2d(x=dfnoise['Col'],y=dfnoise['Row'],bins=35,range=[[-0.5,34.5],[-0.5,34.5]], weights=dfnoise['Masking'], cmap='binary', alpha=0.25)
    fig.colorbar(p6[3], ax=ax[0, 2]).set_label(label='Hits', weight='bold', size=18)
    ax[0, 2].set_xlabel('Col', fontweight = 'bold', fontsize=18)
    ax[0, 2].set_ylabel('Row', fontweight = 'bold', fontsize=18)
    ax[0, 2].xaxis.set_tick_params(labelsize = 18)
    ax[0, 2].yaxis.set_tick_params(labelsize = 18)

    p3 = ax[1, 0].hist2d(x=dfpixel['col'], y=dfpixel['row'], bins=35, range=[[-0.5,34.5],[-0.5,34.5]], weights=dfpixel['norm_sum_avg_tot_us'], cmap='Blues',cmin=1.0, norm=matplotlib.colors.LogNorm())
    fig.colorbar(p3[3], ax=ax[1, 0]).set_label(label='\u03A3 Normalized Time-over-Threshold [us]', weight='bold', size=18)
    ax[1, 0].set_xlabel('Col', fontweight = 'bold', fontsize=18)
    ax[1, 0].set_ylabel('Row', fontweight = 'bold', fontsize=18)
    ax[1, 0].xaxis.set_tick_params(labelsize = 18)
    ax[1, 0].yaxis.set_tick_params(labelsize = 18)

    p4 = ax[1, 1].hist(dffpair['avg_tot_us'], range=(-0.5,25.5), bins=26, color='blue', edgecolor='black', log=False)
    ax[1, 1].set_xlabel('Time-over-Threshold [us]', fontweight = 'bold', fontsize=18)
    ax[1, 1].set_ylabel('Hits', fontweight = 'bold', fontsize=18)
    ax[1, 1].xaxis.set_tick_params(labelsize = 18)
    ax[1, 1].yaxis.set_tick_params(labelsize = 18)

    # Text
    ax[1, 2].set_axis_off()
    ax[1, 2].text(0.1, 0.85, f"Beam: {args.beaminfo}", fontsize=22, fontweight = 'bold');
    ax[1, 2].text(0.1, 0.80, f"ChipID: {args.name}", fontsize=22, fontweight = 'bold');
    ax[1, 2].text(0.1, 0.75, f"Runs: {runnum}", fontsize=22, fontweight = 'bold');
    ax[1, 2].text(0.1, 0.70, f"Events: {tot_n_evts}", fontsize=22, fontweight = 'bold');
    ax[1, 2].text(0.1, 0.60, "Processed below", fontsize=22, fontweight = 'bold');
    ax[1, 2].text(0.1, 0.55, f"conditions: < {args.timestampdiff} timestamp and < {args.totdiff} [us] in ToT", fontsize=22, fontweight = 'bold');
    ax[1, 2].text(0.1, 0.50, f"nevents: {nevents}%", fontsize=22, fontweight = 'bold');
    ax[1, 2].text(0.1, 0.45, f"nhits: {nhits}", fontsize=22, fontweight = 'bold');
    ax[1, 2].text(0.1, 0.40, f"npixels: {npixel}%", fontsize=22, fontweight = 'bold');
    ax[1, 2].text(0.1, 0.35, f"good pixels: {npixels}%", fontsize=22, fontweight = 'bold');

    if args.exclusively:
        ax[0, 0].set_title(f"Number of Hits in 1 x 1 pixel exclusively", fontweight = 'bold', fontsize=18)
        ax[0, 1].set_title(f"Masking map for {args.name}", fontweight = 'bold', fontsize=18)
        ax[0, 2].set_title(f"Number of Hits in 5 x 5 pixels exclusively \n with masking map", fontweight = 'bold', fontsize=18)
        ax[1, 0].set_title(f"Average Time-over-Thresholds in 1 x 1 pixel exclusively", fontweight = 'bold', fontsize=18)
        ax[1, 1].set_title(f"Time-over-Thresholds exclusively", fontweight = 'bold', fontsize=18)
        plt.savefig(f"{args.outdir}/{args.beaminfo}_{args.name}_run_{runnum}_evtdisplay_exclusively.png")
        print(f"{args.outdir}/{args.beaminfo}_{args.name}_run_{runnum}_evtdisplay_exclusively.png was created...")
    else:
        ax[0, 0].set_title(f"Number of Hits in 1 x 1 pixel", fontweight = 'bold', fontsize=18)
        ax[0, 1].set_title(f"Masking map for {args.name}", fontweight = 'bold', fontsize=18)
        ax[0, 2].set_title(f"Number of Hits in 1 x 1 pixels \n with masking map", fontweight = 'bold', fontsize=18)
        ax[1, 0].set_title(f"Average Time-over-Thresholds in 1 x 1 pixel", fontweight = 'bold', fontsize=18)
        ax[1, 1].set_title(f"Time-over-Thresholds", fontweight = 'bold', fontsize=18)
        plt.savefig(f"{args.outdir}/{args.beaminfo}_{args.name}_run_{runnum}_evtdisplay.png")
        print(f"{args.outdir}/{args.beaminfo}_{args.name}_run_{runnum}_evtdisplay.png was created...")
    # Draw Plot
    plt.show()

    # END OF PROGRAM
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Astropix Driver Code')
    parser.add_argument('-n', '--name', default='chip_v3_APS3-W2-S03', required=True,
                    help='chip ID that can be used in name of output file ex) chip230103 or APCv2-230202')

    parser.add_argument('-l','--runnolist', nargs='+', required=True,
                    help = 'List run number(s) you would like to see')

    parser.add_argument('-o', '--outdir', default='/home/labadmin/AstropPix/BeamTest0523/Plots', required=False,
                    help='output directory for all png files')

    parser.add_argument('-d', '--datadir', required=True, default='/home/labadmin/AstropPix/BeamTest0523/BeamData/chip_v3_APS3-W2-S03',
                    help = 'input directory for beam data file')

    parser.add_argument('-s', '--noisedir', required=False, default='/home/labadmin/AstropPix/BeamTest0223/NoiseScan/NoiseMask',
                    help = 'input directory for noise scan summary file to mask pixels')

    parser.add_argument('-t','--noisethreshold', type=int, required=False, default=0,
                    help = 'noise threshold to determine which pixel to be masked')

    parser.add_argument('-td','--timestampdiff', type=float, required=False, default=0.5,
                    help = 'difference in timestamp in pixel matching')
   
    parser.add_argument('-tot','--totdiff', type=float, required=False, default=1.0,
                    help = 'difference in time over threshold [us] in pixel matching')
    
    parser.add_argument('-b', '--beaminfo', default='proton_120GeV', required=False,
                    help='beam information ex) proton_120GeV')

    parser.add_argument('--exclusively', default=False, action='store_true', 
                    help='Throw entire data event if some within event has bad decoding')

    parser.add_argument
    args = parser.parse_args()

    main(args)
