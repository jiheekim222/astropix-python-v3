"""
02/2023 Jihee Kim added making plots from csv file of beam measurements
                  one event(readout) at a time
"""
import argparse
import csv
import matplotlib.pyplot as plt
import pandas as pd

def main(args):

    df = pd.read_csv(args.beamdata)
    print(df)

    dff = df.loc[(df['readout'] == args.evtno) & (df['payload'] == 4)]
    print(dff)

    dffcol = dff.loc[dff['isCol'] == True]
    print(dffcol)

    dffrow = dff.loc[dff['isCol'] == False]
    print(dffrow)

    pair = []
    for indc in dffcol.index:
        for indr in dffrow.index:
            if (dffcol['timestamp'][indc] == dffrow['timestamp'][indr]) & (abs(dffcol['tot_us'][indc] - dffrow['tot_us'][indr]) < 0.3):
                pair.append([dffcol['location'][indc], dffrow['location'][indr], dffcol['timestamp'][indc], dffrow['timestamp'][indr], dffcol['tot_us'][indc], dffrow['tot_us'][indr]])
    
    dffpair = pd.DataFrame(pair, columns=['col', 'row', 'timestamp_col', 'timestamp_row', 'tot_us_col', 'tot_us_row'])
    print(dffpair)

    ax = dffpair.plot.scatter(x='col',y='row',c='tot_us_col',colormap='viridis')
    ax.set_xlim(-1,35)
    ax.set_ylim(-1,35)
    fig = ax.get_figure()
    fig.savefig(f"{args.outdir}/hit_plot_{args.evtno}.png")

    # END OF PROGRAM
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Astropix Driver Code')
    parser.add_argument('-n', '--name', default='', required=False,
                    help='Option to give additional name to output files upon running')

    parser.add_argument('-o', '--outdir', default='.', required=False,
                    help='Output Directory for all datafiles')

    parser.add_argument('-df', '--beamdata', action='store', required=False, type=str, default = 'example_beam_data.csv',
                    help = 'filepath beam data file to be plotted.')

    parser.add_argument('-evt', '--evtno', type=int, action='store', default=None,
                    help = 'event number')

    parser.add_argument
    args = parser.parse_args()

    main(args)
