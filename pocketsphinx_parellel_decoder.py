"""
This decoder is based on pocketsphinx python package.
url: https://pypi.org/project/pocketsphinx/
to install:
python -m pip install --upgrade pip setuptools wheel
sudo apt install libasound2-dev
pip install --upgrade pocketsphinx
"""

import argparse
import datetime
import glob
import multiprocessing
import os
import sys
import time
import configparser
from multiprocessing.pool import Pool

from pocketsphinx import DefaultConfig, Decoder, get_model_path
from pydub import AudioSegment


def load_decoder(model_config):
    # Create a decoder with certain model
    pocketsphinx_config = DefaultConfig()
    model_name = model_config.sections()[0]
    hmm = model_config[model_name]['hmm']
    dict = model_config[model_name]['dict']
    lm = model_config[model_name]['lm']
    logfn = model_config[model_name]['log']
    print('hmm:', hmm)
    print('lm:', lm)
    print('dict:', dict)
    pocketsphinx_config.set_string('-hmm', hmm)
    pocketsphinx_config.set_string('-lm', lm)
    pocketsphinx_config.set_string('-dict', dict)
    pocketsphinx_config.set_string('-logfn', logfn)
    decoder_engine = Decoder(pocketsphinx_config)
    return decoder_engine


def decode_audio(audio_file):
    decode_result = {}
    audio_segment = AudioSegment.from_file(audio_file, format=args.format)
    duration = audio_segment.duration_seconds
    wav_stream = open(audio_file, 'rb')
    my_decoder.start_utt()
    while True:
        buf = wav_stream.read(1024)
        if buf:
            my_decoder.process_raw(buf, False, False)
        else:
            break
    my_decoder.end_utt()
    hypothesis = my_decoder.hyp()
    try:
        text = hypothesis.hypstr
    except AttributeError:
        text = ''
    decode_result[audio_file] = (duration, text)
    return decode_result


def split_list(data, n_parts):
    if len(data) <= n_parts:
        return [data]
    else:
        part_size = int(len(data) / n_parts)
        # print('part size {}'.format(part_size))
        parts = [data[x:x + part_size] for x in range(0, len(data), part_size)]
        if len(parts[-1]) < part_size:
            parts[-2].extend(parts[-1])
            del parts[-1]
        return parts


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for j in range(0, len(l), n):
        yield l[j:j + n]


def split_list_on_cpus(data_list, cpus_number):
    list_size = len(data_list)
    if list_size <= cpus_number:
        return [data_list]
    else:
        return list(chunks(data_list, cpus_number))


parser = argparse.ArgumentParser(description='This decoder is based CMU Sphinx (works offline) engine provided by '
                                             'speech_recognition python package.')  # type: ArgumentParser
parser.add_argument('-i', '--indir', type=str,
                    help='input wave directory', required=True)
parser.add_argument('-c', '--conf', type=str, help='configuration file', required=True)
parser.add_argument('-f', '--format', type=str, choices=['wav', 'mp4'],
                    help='audio format (wav or mp4)', required=True)

if __name__ == '__main__':
    cpu_count = os.cpu_count()
    print('number of CPUs: {}'.format(cpu_count))
    args = parser.parse_args()
    in_dir = args.indir
    audio_files = glob.glob(os.path.join(in_dir, '*.{}'.format(args.format)))
    num_files = len(audio_files)
    if num_files == 0:
        print("no {} found in {}".format(args.format, in_dir))
        sys.exit(-1)
    print('# of audio files: {}'.format(num_files))
    audio_file_lists = split_list_on_cpus(audio_files, cpu_count)
    print('number of parts: {}'.format(len(audio_file_lists)))
    for i, p in enumerate(audio_file_lists):
        print('part {} has {} audio segments'.format(i, len(p)))
    ###################################################
    # load configuration
    config = configparser.ConfigParser()
    conf_file = args.conf
    if not os.path.exists(conf_file):
        print('{} doest not exisit'.format(conf_file))
    config.read(conf_file)
    print('loading decoder models ...')
    my_decoder = load_decoder(config)
    print('decoder has been loaded ...')
    total_duration = 0
    ###################################################
    start_time = time.time()
    # process lists:
    print('processing lists')
    results = {}
    for i, audio_list in enumerate(audio_file_lists):
        print('process {} files in parallel in part {}'.format(len(audio_list), i))
        pool = multiprocessing.Pool(processes=cpu_count)
        result = pool.map(decode_audio, audio_list)
        # print(result)
        for r in result:
            results.update(r)
    ##########################################
    for k, v in results.items():
        print('file: {}'.format(k))
        file_duration, transcription = v
        print('duration: {}'.format(file_duration))
        print('transcription: \n{}'.format(transcription))
        print('######################################')
        total_duration += file_duration

    print('total audio duration: {}'.format(datetime.timedelta(seconds=total_duration)))
    decode_time = time.time() - start_time
    decode_time_str = "decode time: {}".format(datetime.timedelta(seconds=decode_time))
    print(decode_time_str)

"""
How to run: 
python pocketsphinx_parellel_decoder.py -i wav/en -c conf/config_en.ini -f wav 
python pocketsphinx_parellel_decoder.py -i wav/ar -c conf/config_ar.ini -f wav 
python pocketsphinx_parellel_decoder.py -i ~/wav_files_less_than_1m/ -c conf/config_ar.ini -f wav
python cmu-sphinx-decoder/pocketsphinx_parellel_decoder.py -i wav_files_less_than_1m/ -f wav -c cmu-sphinx-decoder/conf/config_ar.ini

"""
