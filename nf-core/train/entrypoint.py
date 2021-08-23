#!/usr/bin/env python3


import os
import shutil
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from subprocess import PIPE, run
import threading

import asyncio
# part of master image
from train_lib.fhir.FhirLoading import genome_query
from train_lib.train.NfcoreTrain import Train


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
    fig.text(0, 0.5, 'Counts', va='center', rotation='vertical')

    plt.suptitle('Top 15 HLA allele counts')

    handles, labels = ax3.get_legend_handles_labels()
    fig.legend(handles, ["Station " + l.split("_")[-1] for l in labels], loc='upper right')
    fig.tight_layout()
    # plt.show()
    fig.savefig(os.path.join(outdir, 'task_b.pdf'))
    print('Task b: plotted results')


def remove(dir):
    try:
        print('Delete: ' + dir)
        shutil.rmtree(dir)
    except OSError as e:
        print('Error: %s - %s.' % (e.filename, e.strerror))


def hla_typing(in_dir, out_dir, work_dir, result_available):
    os.chdir(out_dir)
    command = ['nextflow', 'run', 'nf-core/hlatyping', '-r', '1.2.0', '-c', '/opt/custom_nextflow.config',
               '--input', in_dir, '--out-dir', out_dir]
    if os.path.isdir(out_dir + '/results/optitype'):
        print('Use previous computed HLAtyping results')
    elif os.path.isdir(work_dir):
        print("Resume cached hlatyping ... ")
        command.append('-resume')
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        print(result.returncode, result.stdout, result.stderr)
    else:
        print("Start hlatyping ... may take a while")

        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        print(result.returncode, result.stdout, result.stderr)
        # print(command)
    result_available.set()


if __name__ == "__main__":
    train = Train(results='analysis_results.pkl', query='query.json')  # /opt/pht_train/results/
    results = train.load_results()

    station = str(len(results["exec"])+1)
    print("Start loading patients ... may take a while")
    queries = train.load_queries()
    query = next(iter(queries.values()))
    query = 'Station' + station
    print(query)

    loop = asyncio.get_event_loop()
    pat_df = loop.run_until_complete(genome_query(query))
    input_dir = pat_df['root_path'].value_counts().idxmax() + '/'
    print("FHIR input dir {}".format(input_dir))
    # input_dir = '/data/nftrain-test/*/sequence_read/*_{1,2}.filt.fastq.gz' # test dir pht-demo server
    print(input_dir)


    print('Previous results:\n' + str(results))
    #station = input_dir[-2]

    # HLAtyping
    result_available = threading.Event()

    input_dir = "/mnt/vdb/data/station_" + station + "/*/sequence_read/*_{1,2}.filt.fastq.gz"

    out_dir = "/mnt/vdb/data/exec_" + station

    if not os.path.isdir(out_dir):
        print("Create: {}".format(out_dir))
        os.makedirs(out_dir)
    print("Exists: {}".format(out_dir))
    work_dir = out_dir + "/work"

    # get list of result files from different subdirectories
    results_dir = out_dir + "/results/optitype/"
    # print(results_dir)

    thread = threading.Thread(target=hla_typing(input_dir, out_dir, work_dir, result_available))

    thread.start()
    result_available.wait()
    print('HLA typing finished')

    files = list(Path(results_dir).rglob('*.tsv'))
    # print(files)
    try:
        # create dataframe from OptiType results
        results_df = pd.concat([pd.read_csv(f, sep='\t', usecols=["A1", "A2", "B1", "B2", "C1", "C2"]) for f in
                                files], ignore_index=True)
    except:
        print("No results from hlatyping")
        exit(1)

    print(results_df.describe())

    # task a
    allele = 'B*35:01'  # prev A*11:01
    sub_allele = ['B1', 'B2']
    # out_dir = '/opt/pht_train/endpoints/hlatyping/commands/run/'

    print('Task a: Check allele occurrences')
    local_res = 0
    for group in sub_allele:
        sub_group = results_df[group].value_counts()
        try:
            local_res += int(sub_group[allele])
        except Exception as e:
            print(e)
            print("No occurence of {} on allel {}".format(allele, group))

    he_secure_add = train.secure_addition(local_res)
    print("Secure addition added local result {} in encrypted format and saved:\n{}".format(local_res, he_secure_add))

    # task b - Plot top 15 alleles

    # store station specific frequencies for later
    a_freqs = compute_freqs(results_df, "A1", "A2")
    b_freqs = compute_freqs(results_df, "B1", "B2")
    c_freqs = compute_freqs(results_df, "C1", "C2")

    frame_data = {'A_{}'.format(station): a_freqs, 'B_{}'.format(station): b_freqs,
                  'C_{}'.format(station): c_freqs}

    plot_df = pd.DataFrame(frame_data)

    try:
        previous_result = results['analysis']['task_b']
        merged_result = previous_result.combine_first(plot_df)
    except KeyError:
        print("Task b: No previous results to load")
        merged_result = plot_df

    # os.chdir(train_work_dir)

    # merged_result.to_csv(os.path.join(results_dir, tmp_res_file_b))
    generate_plot(merged_result.filter(like='A*', axis=0).filter(like='A_', axis=1),
                  merged_result.filter(like='B*', axis=0).filter(like='B_', axis=1),
                  merged_result.filter(like='C*', axis=0).filter(like='C_', axis=1),
                  '/opt/pht_results/')  # old: /data/station_1/ new: out dir train = /opt/pht_results/

    # clean up
    remove(work_dir)
    results['analysis']['task_a'] = he_secure_add
    if station == str(3):
        print("Final execution")
        results.pop('task_b')
        results.pop('exec')
    else:
        print("Keep intermediate task b data")
        results['analysis']['task_b'] = merged_result
    results["exec"].append(1)
    train.save_results(results=results)
    print('New results:\n' + str(results) + "\nupdated and files saved")

    del queries[next(iter(queries))]  # delete first entry
    train.save_queries(queries)
