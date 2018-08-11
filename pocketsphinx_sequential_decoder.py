

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
import io
import os
import sys
import time
import logging


from pocketsphinx import DefaultConfig, Decoder
from pydub import AudioSegment
import decoderUtils

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)

parser = argparse.ArgumentParser(description='This decoder is based CMU Sphinx (works offline) engine provided by '
                                             'speech_recognition python package.')  # type: ArgumentParser
parser.add_argument('-i', '--indir', type=str,
                    help='input wave directory', required=True)
parser.add_argument('-c', '--conf', type=str, help='configuration file', required=True)
parser.add_argument('-l', '--log', action='store_true')
# parser.add_argument('-o', '--outdir', type=str, help='output directory')


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


if __name__ == '__main__':
    cpu_count = os.cpu_count()
    print('number of CPUs: {}'.format(cpu_count))
    args = parser.parse_args()
    in_dir = args.indir
    audio_files = sorted(glob.glob(os.path.join(in_dir, '*.*')))
    num_files = len(audio_files)
    if num_files == 0:
        print("no files found in {}".format(in_dir))
        sys.exit(-1)
    print('# of audio files: {}'.format(num_files))
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
    for i, audio_file in enumerate(audio_files):
        if args.log:
            logging.info('decode {}'.format(audio_file))
        result = decode_audio(audio_file, my_decoder)
        results.update(result)
    ##########################################
    decoderUtils.print_results(sorted(results), in_dir)
    print('done!')

"""
How to run: 
source ~/py3env/bin/activate
python ~/PycharmProjects/cmu-sphinx-decoder/pocketsphinx_sequential_decoder.py -i ~/ts_sample_files/wav -c ~/PycharmProjects/cmu-sphinx-decoder/conf/config_ar.ini 



~/ts_sample_files/wav
total audio duration: 0:01:30.005625
total decode time: 0:01:13.909128
total conversion time: 0:00:00

source ~/py3env/bin/activate
python ~/PycharmProjects/cmu-sphinx-decoder/pocketsphinx_sequential_decoder.py -i ~/wav_files_less_than_1m -c ~/PycharmProjects/cmu-sphinx-decoder/conf/config_ar.ini 

~/wav_files_less_than_1m
total audio duration: 0:06:06.040000
total decode time: 0:04:10.761857
total conversion time: 0:00:00



"""
