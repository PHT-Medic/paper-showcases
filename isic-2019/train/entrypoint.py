#!/usr/bin/env python
import pickle
from dotenv import load_dotenv, find_dotenv
import os
import urllib3
import ast
from requests.auth import HTTPBasicAuth
import requests
from train import training
import os
import sys
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
import torch

import asyncio
from train_lib.fhir.FhirLoading import isic_query
from train_lib.train.ISICTrain import Train
from glob import glob


if __name__ == "__main__":
    train = Train(results='results.pkl', query='query.json')  # /opt/pht_train/results/
    results = train.load_results()
    queries = train.load_queries()
    station = str(len(results["exec"]) + 1)

    print("Start loading patients ... may take a while")
    query = 'station_' + station
    print(query)

    loop = asyncio.get_event_loop()
    pat_df = loop.run_until_complete(isic_query(query))

    results = train.discovery(pat_df, results)
    train.plot_discovery_results(results['discovery'])

    path_labels = "/mnt/vdb/data/isic/2019/labels/official/"

    try:
        old_labels_list = glob(path_labels + '*.csv')
        _, old_label_fn = os.path.split(old_labels_list[0])
        train.move_file(old_labels_list[0], '/mnt/vdb/data/isic/2019/curr_unused_labels/' + old_label_fn)
        print('Old label file moved')
    except Exception:
        print('Old label file moved and deleted')
    labels = train.create_label_file(pat_df, path_labels, station)

    save_folder = 'effb6_s'+str(station)+'_equaldist'

    if station == str(1):
        performance = training(cfgs_name='example', save_dir=save_folder, gpus='gpu=0,1', prev_station=None)
    else:
        prev_model = glob('/opt/pht_results/**_best**.pt')
        print('Prev_model {}'.format(prev_model[0]))
        performance = training(cfgs_name='example', save_dir=save_folder, gpus='gpu=0,1', prev_station=prev_model[0])

        os.remove(prev_model[0])
    print(performance)

    # Find best CV Fold bases on F1 score performance
    best_cv = train.find_best_cv(performance)

    path_best_model = glob('/mnt/vdb/data/isic/' + save_folder + '/CVSet' + str(best_cv) + '/**_best**.pt')
    _, best_model_name = os.path.split(path_best_model[0])
    # Copy best model of current station to train directory
    print('Copy best model of current station to train directory')
    _ = train.copy_file(path_best_model[0], '/opt/pht_results/' + best_model_name)

    # Find all mat files and move performance of each fold to train
    mat_files = glob('/mnt/vdb/data/isic/' + save_folder + '/**/*.mat')

    train.create_stat_res_dirs(station)

    for i, mat_file in enumerate(mat_files):
        _, file_name = os.path.split(mat_file)
        dest_file = '/opt/pht_results/res_' + str(station) + '/mat_' + str(i) + file_name
        train.copy_file(mat_file, dest_file)
        print('Copied file {} from to {}'.format(mat_file, dest_file))

    if station == str(3):
        print("Final execution - remove temporary files")
        # plot results
        routes = [['/opt/pht_results/res_1',
                   '/opt/pht_results/res_2',
                   '/opt/pht_results/res_3']]
        train.plot_stations(routes, ['acc', 'sens'], '/opt/pht_results/distributed_train_performance.png', smoothing_factor=.5, save=True, num_stations=3)

        results['analysis']['regular_exec_' + str(station)] = performance
        results.pop('exec')
        # Remove mat files with performance of plots
        for tmp_res_dir in routes[0]:
            train.clean_up(tmp_res_dir)
    else:
        print(results)
        results['analysis']['regular_exec_' + str(station)] = performance
        results["exec"].append(1)

    train.save_results(results=results)
    print('New results:\n' + str(results) + "\nupdated and files saved")

    train.save_queries(queries)
    # clean up
    # if train.clean_up('/mnt/vdb/data/isic/' + save_folder):
    #    exit(0)
    exit(0)
