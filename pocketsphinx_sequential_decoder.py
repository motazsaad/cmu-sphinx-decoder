"""
This decoder is based on pocketsphinx python package.
url: https://pypi.org/project/pocketsphinx/
to install:
python -m pip install --upgrade pip setuptools wheel
sudo apt install libasound2-dev
pip install --upgrade pocketsphinx
"""

# pocketsphinx batch vs continuous:
# https://github.com/cmusphinx/pocketsphinx/issues/116


import argparse
import configparser
import datetime
import glob
import logging
import os
import sys

import decoderUtils

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)

parser = argparse.ArgumentParser(description='This decoder is based CMU Sphinx (works offline) engine '
                                             'provided by speech_recognition python package.')  # type: ArgumentParser
parser.add_argument('-i', '--indir', type=str, help='input wave directory', required=True)
parser.add_argument('-c', '--conf', type=str, help='configuration file', required=True)
parser.add_argument('-l', '--log', action='store_true')
parser.add_argument('-o', '--outdir', type=str, help='output file name prefix', required=True)
parser.add_argument('-s', '--srate', type=str, help='sample rate for the converted wav', default='16000')


if __name__ == '__main__':
    cpu_count = os.cpu_count()
    print('number of CPUs: {}'.format(cpu_count))
    ###########################################
    # parse args
    args = parser.parse_args()
    in_dir = args.indir
    conf_file = args.conf
    log = args.log
    outdir = args.outdir
    out = os.path.join(os.path.normpath(outdir),
                       in_dir.replace('/storage/recordings/', '').replace('/', '_'))
    out = out + '_' + os.path.basename(conf_file)
    ts = time.time()
    time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M')
    out = out + '_' + time_stamp
    sample_rate = args.srate
    ###########################################
    config = configparser.ConfigParser()
    if not os.path.exists(conf_file):
        print('ERROR: {} doest not exisit'.format(conf_file))
        sys.exit(-1)
    config.read(conf_file)
    if log:
        logging.info('config file: {}'.format(conf_file))
    model_name = config.sections()[0]
    hmm = config[model_name]['hmm']
    dict = config[model_name]['dict']
    lm = config[model_name]['lm']
    # logfn = config[model_name]['log']
    logfn = out + '.log'
    print('hmm: {}'.format(hmm))
    print('dict: {}'.format(dict))
    print('lm: {}'.format(lm))
    print('logfn: {}'.format(logfn))
    ###########################################
    audio_files = sorted(glob.glob(os.path.join(in_dir, '*.*')))
    num_files = len(audio_files)
    if num_files == 0:
        print("no files found in {}".format(in_dir))
        sys.exit(-1)
    print('# of audio files: {}'.format(num_files))
    ###################################################
    ###################################################
    decoderUtils.decode_speech("seq", audio_files, config, in_dir, out, log, sample_rate)

