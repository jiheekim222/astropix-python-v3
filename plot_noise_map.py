"""
02/2023 Jihee Kim added making plots from csv file of noise scan measurements
"""
import argparse
import csv
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
import glob
plt.style.use('classic')

def main(args):
   
    # Path to noise scan data location
    path = args.noisedir
    # Find noise scan data and Read
    filename = args.noisedir + '/noise_scan_summary_' + args.name +'*.csv'
    file = glob.glob(filename)
    for f in file:
        df = pd.read_csv(f)
    # Add new columns for masking
    df['Stringent Masking'] = 0
    df['Stringent Masking'] = np.where(df['Count'] > 0, 1, df['Stringent Masking']) 
    df['Masking'] = 0
    df['Masking'] = np.where(df['Count'] > args.noisethreshold, 1, df['Masking']) 
    # Calculate how many pixels are good
    s_npixels = '%.2f' % ((df['Stringent Masking'].value_counts()[0]/df.shape[0]) * 100.)
    npixels = '%.2f' % ((df['Masking'].value_counts()[0]/df.shape[0]) * 100.)
    print('The first 5 noisy pixels:')
    print(df.nlargest(10, 'Count'))
    # Generate figures
    # Noise map
    fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, figsize=(25, 6))
    p1 = ax1.hist2d(x=df['Col'],y=df['Row'],bins=35,range=[[-0.5,34.5],[-0.5,34.5]], weights=df['Count'], cmap='viridis',cmin=1.0)
    fig.colorbar(p1[3], ax=ax1).set_label(label='Hits', size=15)
    ax1.set_xlabel('Col', fontsize=15)
    ax1.set_ylabel('Row', fontsize=15)
    ax1.set_title(f"{args.name} noise map \n voltage threshold {args.voltagethreshold} mV", fontsize=15)
    # Stringent masking map
    p2 = ax2.hist2d(x=df['Col'],y=df['Row'],bins=35,range=[[-0.5,34.5],[-0.5,34.5]], weights=df['Stringent Masking'], cmap='binary')
    fig.colorbar(p2[3], ax=ax2).set_label(label='Masking', size=15)
    ax2.set_xlabel('Col', fontsize=15)
    ax2.set_ylabel('Row', fontsize=15)
    ax2.set_title(f"{args.name} masking map \n with noise threshold 0 ({s_npixels}%)", fontsize=15)
    # Masking map with input noise threshold
    p3 = ax3.hist2d(x=df['Col'],y=df['Row'],bins=35,range=[[-0.5,34.5],[-0.5,34.5]], weights=df['Masking'], cmap='binary')
    fig.colorbar(p3[3], ax=ax3).set_label(label='Masking', size=15)
    ax3.set_xlabel('Col', fontsize=15)
    ax3.set_ylabel('Row', fontsize=15)
    ax3.set_title(f"{args.name} masking map \n with noise threshold {args.noisethreshold} ({npixels}%)", fontsize=15)
    # Draw figure
    plt.show()
    # Save figure 
    plt.savefig(f"{args.outdir}/{args.name}_noise_map_nt_{args.noisethreshold}_vt_{args.voltagethreshold}.png")
    
    # END OF PROGRAM
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Astropix Driver Code')
    parser.add_argument('-n', '--name', default='APS3-W2-S03', required=True,
                    help='chip ID that can be used in name of output file')
    
    parser.add_argument('-o', '--outdir', default='/home/labadmin/AstropPix/BeamTest2023/Plots', required=True,
                    help='output directory for all png files')
    
    parser.add_argument('-s', '--noisedir', action='store', required=True, default = '/home/labadmin/AstropPix/BeamTest2023/NoiseScan',
                    help = 'input directory for noise scan summary file to mask pixels')

    parser.add_argument('-t','--noisethreshold', type=int, required=True, default=5,
                    help = 'noise threshold to determine which pixel to be masked')
    
    parser.add_argument('-vt','--voltagethreshold', type=int, required=False, default=100,
                    help = 'voltage threshold to pixel')
    
    parser.add_argument
    args = parser.parse_args()

    main(args)
