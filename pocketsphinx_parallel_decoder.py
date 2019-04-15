"""
This decoder is based on pocketsphinx python package.
url: https://pypi.org/project/pocketsphinx/
to install:
python -m pip install --upgrade pip setuptools wheel
sudo apt install libasound2-dev
pip install --upgrade pocketsphinx
"""
import argparse
import configparser
import datetime
import glob
import logging
import os
import sys
import time
from multiprocessing import Process

import decoderUtils

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)

parser = argparse.ArgumentParser(description='This decoder is based CMU Sphinx'
                                             ' (works offline) engine provided by'
                                             ' speech_recognition python package.')
parser.add_argument('-i', '--indir', type=str, help='input wave directory', required=True)
parser.add_argument('-c', '--conf', type=str, help='configuration file', required=True)
parser.add_argument('-l', '--log', action='store_true')
parser.add_argument('-j', '--jobs', type=int, help='number of parallel jobs. Default= # of CPUs')
parser.add_argument('-o', '--outdir', type=str, help='output output directory', required=True)
parser.add_argument('-s', '--srate', type=str, help='sample rate for the converted wav', default='16000')

if __name__ == '__main__':
    ###########################################
    # parse args
    args = parser.parse_args()
    in_dir = args.indir
    conf_file = args.conf
    log = args.log
    outdir = args.outdir
    out = os.path.join(os.path.normpath(outdir),
                       in_dir.replace('/storage/recordings/', '').replace('/', '_'))
    ##############################
    indir_date = in_dir.replace('/storage/recordings/', '').replace('/', '_')
    outfile = '/home/sphinxuser/logs/' + indir_date + '.log'
    progress_outfile = '/home/sphinxuser/logs/' + indir_date + '_progress.log'
    sys.stdout = open(outfile, mode='w', encoding='utf-8')
    print('outfile', outfile)
    print('indir date:', indir_date)
    ##############################
    out = out + '_' + os.path.basename(conf_file)
    ts = time.time()
    time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%Hh%M')
    out = out + '_' + time_stamp
    sample_rate = args.srate
    cpu_count = os.cpu_count()
    print('number of CPUs: {}'.format(cpu_count))
    if args.jobs:
        jobs = args.jobs
        if jobs > cpu_count:
            print('ERROR: # of jobs must be < {}'.format(cpu_count))
            sys.exit(-1)
    else:
        jobs = cpu_count
    ###########################################
    config = configparser.ConfigParser()
    if not os.path.exists(conf_file):
        print('ERROR: {} doest not exist'.format(conf_file))
        sys.exit(-1)
    config.read(conf_file)
    if log:
        logging.info('config file: {}'.format(conf_file))
    model_name = config.sections()[0]
    hmm = config[model_name]['hmm']
    dic = config[model_name]['dict']
    lm = config[model_name]['lm']
    # logfn = config[model_name]['log']
    # logfn = out + '.log'
    print('hmm: {}'.format(hmm))
    print('dict: {}'.format(dic))
    print('lm: {}'.format(lm))
    print('audio directory: {}'.format(in_dir))
    # print('logfn: {}'.format(logfn))
    ###########################################
    audio_files = sorted(glob.glob(os.path.join(in_dir, '*.*')))
    num_files = len(audio_files)
    if num_files == 0:
        print("no files found in {}".format(in_dir))
        sys.exit(-1)
    print('# of audio files: {}'.format(num_files))
    ###################################################
    audio_file_lists = decoderUtils.split_n_lists_uniform(audio_files, jobs)
    print('number of parts: {}'.format(len(audio_file_lists)))
    logging.info("start the process")
    start = time.time()
    processes = list()
    for i, audio_list in enumerate(audio_file_lists):
        print('part {} has {} audio segments'.format(i, len(audio_list)))
        proc = Process(target=decoderUtils.decode_speech,
                       args=(i, audio_list, config, in_dir,
                             out, log, sample_rate, progress_outfile))
        processes.append(proc)
        proc.start()
    for p in processes:
        p.join()
    end = time.time()
    print('\n\n\n\n\n\n\n\n\n')
    print('TOTAL TIME: {:.2f} minutes'.format(((end - start) / 60)))
    logging.info("done")
