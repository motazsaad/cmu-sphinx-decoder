

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
import io
import multiprocessing
import os
import sys
import time
import configparser

from pocketsphinx import DefaultConfig, Decoder, get_model_path
from pydub import AudioSegment

import decoderUtils


def decode_audio(audio_file):
    decode_result = {}
    audio_segment = AudioSegment.from_file(audio_file)
    # audio_segment = audio_segment.set_frame_rate(16000)
    # audio_segment = audio_segment.set_channels(1)
    duration = audio_segment.duration_seconds
    conversion_time = 0
    if not audio_file.endswith('.wav'):
        conversion_start_time = datetime.time.time()
        # print('converting {} to wav'.format(audio_file))
        wav_in_ram = io.BytesIO()
        # data = audio_segment.raw_data
        # wav_in_ram.write(data)
        # wav_in_ram.seek(0)
        audio_segment = audio_segment.set_frame_rate(16000)
        audio_segment = audio_segment.set_channels(1)
        print('ar: {}: ac: {} file: {}'.
              format(audio_segment.frame_rate, audio_segment.channels, audio_file))
        audio_segment.export(wav_in_ram, format="wav")
        tmp_file_name = '/home/motaz/tmp/exported_waves/' + os.path.basename(audio_file) + '.wav'
        audio_segment.export(tmp_file_name, format="wav")
        wav_in_ram.seek(0)
        wav_stream = wav_in_ram
        conversion_time = time.time() - conversion_start_time
        # print('{} has been converted to wav'.format(audio_file))
    else:
        wav_stream = open(audio_file, 'rb')
    decode_time_start_time = datetime.time.time()
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
    decode_time = time.time() - decode_time_start_time
    decode_result[audio_file] = (duration, decode_time, conversion_time, text)
    return decode_result


parser = argparse.ArgumentParser(description='This decoder is based CMU Sphinx (works offline) engine provided by '
                                             'speech_recognition python package.')  # type: ArgumentParser
parser.add_argument('-i', '--indir', type=str, help='input wave directory', required=True)
parser.add_argument('-c', '--conf', type=str, help='configuration file', required=True)
parser.add_argument('-o', '--outdir', type=str, help='output directory')

if __name__ == '__main__':
    cpu_count = os.cpu_count()
    print('number of CPUs: {}'.format(cpu_count))
    args = parser.parse_args()
    in_dir = args.indir
    audio_files = sorted(glob.glob(os.path.join(in_dir, '*.*')))[:5]
    num_files = len(audio_files)
    if num_files == 0:
        print("no files found in {}".format(in_dir))
        sys.exit(-1)
    print('# of audio files: {}'.format(num_files))
    audio_file_lists = decoderUtils.split_list_on_cpus(audio_files, cpu_count)
    print('number of parts: {}'.format(len(audio_file_lists)))
    for i, p in enumerate(audio_file_lists):
        print('part {} has {} audio segments'.format(i, len(p)))
    ###################################################
    # load configuration
    config = configparser.ConfigParser()
    conf_file = args.conf
    if not os.path.exists(conf_file):
        print('ERROR: {} doest not exisit'.format(conf_file))
        sys.exit(-1)
    config.read(conf_file)
    print('loading decoder models ...')
    my_decoder = decoderUtils.load_decoder(config)
    print('decoder has been loaded ...')
    ###################################################
    # process lists:
    print('processing lists')
    print('input directory: {}'.format(in_dir))
    results = {}
    for i, audio_list in enumerate(audio_file_lists):
        print('process {} files in parallel in part {}'.format(len(audio_list), i))
        pool = multiprocessing.Pool(processes=cpu_count)
        result = pool.map(decode_audio, audio_list)
        # print(result)
        for r in result:
            results.update(r)
    ##########################################
    decoderUtils.print_results(sorted(results), in_dir)
    print('done!')
    ##########################################


"""
How to run: 
python pocketsphinx_parallel_decoder.py -i wav/en -c conf/config_en.ini 
python pocketsphinx_parallel_decoder.py -i wav/ar -c conf/config_ar.ini
python pocketsphinx_parallel_decoder.py -i ~/wav_files_less_than_1m/ -c conf/config_ar.ini
python cmu-sphinx-decoder/pocketsphinx_parallel_decoder.py -i wav_files_less_than_1m/ -c cmu-sphinx-decoder/conf/config_ar.ini
python pocketsphinx_parallel_decoder.py -i ~/ts_sample_files/ -c conf/config_ar.ini

python pocketsphinx_parallel_decoder.py -i ~/PycharmProjects/jsc-news-broadcast/mp3/ -c conf/config_ar.ini


python cmu-sphinx-decoder/pocketsphinx_parallel_decoder.py -i jsc-news-broadcast/wav_split/headlines_10pm_29_07_2017/mp3/ -c cmu-sphinx-decoder/conf/config_ar.ini -o out

source ~/py3env/bin/activate
python ~/PycharmProjects/cmu-sphinx-decoder/pocketsphinx_parallel_decoder.py -i ~/PycharmProjects/jsc-news-broadcast/wav_split/headlines_10pm_29_07_2017/mp3/wav -c ~/PycharmProjects/cmu-sphinx-decoder/conf/config_ar.ini -o out


source ~/py3env/bin/activate
python ~/PycharmProjects/cmu-sphinx-decoder/pocketsphinx_parallel_decoder.py -i ~/ts_sample_files/ -c ~/PycharmProjects/cmu-sphinx-decoder/conf/config_ar.ini -o out 

source ~/py3env/bin/activate
python ~/PycharmProjects/cmu-sphinx-decoder/pocketsphinx_parallel_decoder.py -i ~/ts_sample_files/wav -c ~/PycharmProjects/cmu-sphinx-decoder/conf/config_ar.ini -o out 

"""
