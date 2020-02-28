#!/usr/bin/env python3

import os
import shutil
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from subprocess import PIPE, run
import threading


"""entrypoint.py: Demonstration of hlatyping pipeline.
Downstream analysis of HLA typing results of OptiType. Merges previous results if available."""


typing_done = threading.Event()


def run_hla_typing(path):
    try:
        command = ['nextflow', 'run', 'nf-core/hlatyping', '--reads', path,  '--out-dir', './results']
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        print(result.returncode, result.stdout, result.stderr)
        typing_done.set()
    except result.stderr as e:
        print('Error hlatyping {}'.format(e))



def compute_freqs(df, key1, key2):
    return df[key1].value_counts().add(df[key2].value_counts(), fill_value=0)


def generate_plot(a_freqs, b_freqs, c_freqs, outdir):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    plt.subplots_adjust(hspace=0.9)

    plt.setp(ax1.get_xticklabels(), fontsize=8, horizontalalignment="left", rotation=45)
    plt.setp(ax2.get_xticklabels(), fontsize=8, horizontalalignment="left", rotation=45)
    plt.setp(ax3.get_xticklabels(), fontsize=8, horizontalalignment="left", rotation=45)

    # add total counts column, sorting and plot
    a_freqs.loc[:, 'total'] = a_freqs.sum(numeric_only=True, axis=1)
    a_freqs = a_freqs.sort_values(by='total', ascending=False)
    a_freqs = a_freqs.drop('total', axis=1)
    a_freqs[:15].plot.bar(ax=ax1, stacked=True, legend=False)

    b_freqs.loc[:, 'total'] = b_freqs.sum(numeric_only=True, axis=1)
    b_freqs = b_freqs.sort_values(by='total', ascending=False)
    b_freqs = b_freqs.drop('total', axis=1)
    b_freqs[:15].plot.bar(ax=ax2, stacked=True, legend=False)

    c_freqs.loc[:, 'total'] = c_freqs.sum(numeric_only=True, axis=1)
    c_freqs = c_freqs.sort_values(by='total', ascending=False)
    c_freqs = c_freqs.drop('total', axis=1)
    c_freqs[:15].plot.bar(ax=ax3, stacked=True, legend=False)

    ax1.set(ylabel="HLA-A")
    ax2.set(ylabel="HLA-B")
    ax3.set(ylabel="HLA-C")

    plt.suptitle('Top 15 HLA allele counts')

    handles, labels = ax3.get_legend_handles_labels()
    fig.legend(handles, [l.split("_")[-1] for l in labels], loc='upper right')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    fig.savefig(os.path.join(outdir, 'HLA_frequencies.pdf'))
    print('Task b: plotted results')


def task_a(in_list, patients):
    res_name = in_list[0]
    allele = in_list[1]
    section = in_list[2]
    out_dir = in_list[3]
    sub_group = patients[section].value_counts()

    results_available = res_name in os.listdir(out_dir)

    if results_available:
        with open(res_name, 'r') as f:
            allele_count = int(f.read())
        f.close()
    else:
        allele_count = 0

    print('Task a: Check allele occurrences')

    allele_count += int(sub_group[allele])
    final_res = str(allele_count)

    with open(res_name, 'w') as f:
        f.write('{}\n'.format(final_res))
    f.close()
    print(final_res)


def task_b(res_name_b, station_id, hla_res_dir, results_df, work_dir):
    results_available = res_name_b in os.listdir(work_dir)

    # store station specific frequencies for later
    a_freqs = compute_freqs(results_df, "A1", "A2")
    b_freqs = compute_freqs(results_df, "B1", "B2")
    c_freqs = compute_freqs(results_df, "C1", "C2")

    frame_data = {'A_{}'.format(station_id): a_freqs, 'B_{}'.format(station_id): b_freqs,
                  'C_{}'.format(station_id): c_freqs}

    dataframe = pd.DataFrame(frame_data)
    if results_available:
        previous_result = pd.read_csv(os.path.join(work_dir, res_name_b), index_col=0)
        merged_result = previous_result.combine_first(dataframe)
    else:
        merged_result = dataframe

    merged_result.to_csv(os.path.join(hla_res_dir, res_name_b))
    generate_plot(merged_result.filter(like='A*', axis=0).filter(like='A_', axis=1),
                  merged_result.filter(like='B*', axis=0).filter(like='B_', axis=1),
                  merged_result.filter(like='C*', axis=0).filter(like='C_', axis=1),
                  work_dir)


def run_analysis(hla_dir, task_a_in_list, task_b_in_list):
    thread = threading.Thread(target=run_hla_typing(hla_dir))

    thread.start()
    typing_done.wait()

    res_name_b = task_b_in_list[0]
    hla_res_dir = task_b_in_list[1]
    station_id = task_b_in_list[2]
    work_dir = task_b_in_list[3]

    # get list of result files from different subdirectories
    files = list(Path(hla_res_dir).rglob('*.tsv'))

    # create dataframe from OptiType results
    try:
        results_df = pd.concat([pd.read_csv(f, sep='\t', usecols=["A1", "A2", "B1", "B2", "C1", "C2"]) for f in
                                files], ignore_index=True)

    except ValueError as e:
        print(e)
        exit(1)
    # Count allele
    task_a(task_a_in_list, results_df)

    # Plot top 15 alleles
    task_b(res_name_b, station_id, hla_res_dir, results_df, work_dir)


def remove(dirs):
    for d in dirs:
        try:
            shutil.rmtree(d)
            print('Deleted: ' + d)
        except OSError as e:
            print('Error: %s - %s.' % (e.filename, e.strerror))


def remove_tmp(dirs, file, last_exec):
    if last_exec:
        remove(dirs)
        os.remove(file)
    else:
        remove(dirs)


def main():
    # input hlatyping
    hla_dir = '/data/*/sequence_read/*_{1,2}.filt.fastq.gz'
    #hla_dir = '"/Users/mariusherr/Documents/GitHub/showcases/qbic/data_preperation/data/station_2/*/sequence_read/*_{1,2}.filt.fastq"'
    station = 1

    # input task a
    tmp_res_file_a = 'task_a_result.txt'
    allele = 'A*11:01'
    sub_allele = 'A1'
    out_dir = '/opt/pht_train/'
    task_a_in = [tmp_res_file_a, allele, sub_allele, out_dir]

    # input task b
    res_folder = '/opt/pht_train/results_' + str(station)
    res_dir = res_folder + '/optitype/'
    tmp_res_file_b = 'task_b_tmp_result.csv'
    task_b_in = [tmp_res_file_b, res_dir, station, out_dir]

    # run analysis and tasks
    run_analysis(hla_dir, task_a_in, task_b_in)

    # remove files from hlatyping
    # TODO when used on workstation only the result folder necessary to remove
    folders_to_remove = ['/opt/pht_train/work', res_folder]

    last_exec = True
    remove_tmp(folders_to_remove, tmp_res_file_b, last_exec)


if __name__ == "__main__":
    main()

