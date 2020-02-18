#!/usr/bin/env python

"""analyze_hla_typings.py: Downstream analysis of HLA typing results of OptiType. Merges previous results if available."""

import os
import argparse
import csv
import glob
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt


def compute_freqs(df, key1, key2):
    return df[key1].value_counts().add(df[key2].value_counts(), fill_value=0)

def generate_plot(a_freqs, b_freqs, c_freqs, outdir):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    plt.subplots_adjust(hspace = 0.9)

    plt.setp(ax1.get_xticklabels(), fontsize=8, horizontalalignment="left", rotation=45)
    plt.setp(ax2.get_xticklabels(), fontsize=8, horizontalalignment="left", rotation=45)
    plt.setp(ax3.get_xticklabels(), fontsize=8, horizontalalignment="left", rotation=45)

    a_freqs.plot.bar(ax=ax1, stacked=True, legend=False)
    b_freqs.plot.bar(ax=ax2, stacked=True, legend=False)
    c_freqs.plot.bar(ax=ax3, stacked=True, legend=False)

    ax1.set(ylabel="HLA-A")
    ax2.set(ylabel="HLA-B")
    ax3.set(ylabel="HLA-C")

    plt.suptitle('HLA allele frequency')

    handles, labels = ax3.get_legend_handles_labels()
    fig.legend(handles, [l.split("_")[-1] for l in labels], loc='upper right')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    fig.savefig(os.path.join(outdir, 'HLA_frequencies.pdf'))


def main():
    parser = argparse.ArgumentParser("Downstream analysis for PHT processed HLA typing results.")
    parser.add_argument("-s", "--station", type=str,
                    help="name of station (will be used in plot)", required=True)
    parser.add_argument("-d", "--directory", type=str,
                    help="path to directory with HLA typing results", required=True)
    parser.add_argument("-o", "--outdir", type=str,
                    help="path to directory where merged results should be stored", required=True)
    args = parser.parse_args()

    results_available = "merged_results.csv" in os.listdir(args.outdir)

    # create dataframe from OptiType results
    results_df = pd.concat([pd.read_csv(f, sep='\t', usecols=["A1","A2","B1","B2","C1","C2"]) for f in glob.glob(os.path.join(args.directory,'*.tsv'))], ignore_index = True)

    a_freqs = compute_freqs(results_df, "A1", "A2")
    b_freqs = compute_freqs(results_df, "B1", "B2")
    c_freqs = compute_freqs(results_df, "C1", "C2")

    # store station specific frequencies for later 
    frame_data = { 'A_{}'.format(args.station): a_freqs, 'B_{}'.format(args.station): b_freqs, 'C_{}'.format(args.station): c_freqs}
    dataframe = pd.DataFrame(frame_data)
    if results_available:
        previous_result = pd.read_csv(os.path.join(args.outdir, "merged_results.csv"), index_col=0)  
        merged_result = previous_result.combine_first(dataframe)
    else:
        merged_result = dataframe
        
    merged_result.to_csv(os.path.join(args.outdir, "merged_results.csv"))
    generate_plot(merged_result.filter(like='A*', axis=0).filter(like='A_', axis=1), merged_result.filter(like='B*', axis=0).filter(like='B_', axis=1) ,merged_result.filter(like='C*', axis=0).filter(like='C_', axis=1), args.outdir)

if __name__ == "__main__":
    main()