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
import os
import sys
import time
import configparser

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


def decode_wave(wave, wav_decoder):
    wav_decoder.start_utt()
    stream = wave
    while True:
        buf = stream.read(1024)
        if buf:
            wav_decoder.process_raw(buf, False, False)
        else:
            break
    wav_decoder.end_utt()
    hypothesis = wav_decoder.hyp()
    try:
        message = hypothesis.hypstr
    except AttributeError:
        message = ''
    return message


parser = argparse.ArgumentParser(description='This decoder is based CMU Sphinx (works offline) engine provided by '
                                             'speech_recognition python package.')  # type: ArgumentParser
parser.add_argument('-i', '--indir', type=str,
                    help='input wave directory', required=True)
parser.add_argument('-c', '--conf', type=str, help='configuration file', required=True)
parser.add_argument('-f', '--format', type=str,
                    help='audio format (wav or mp4)', required=True)

if __name__ == '__main__':
    cpu_count = os.cpu_count()
    print('number of CPUs: {}'.format(cpu_count))
    config = configparser.ConfigParser()
    start_time = time.time()
    args = parser.parse_args()
    wav_dir = args.indir
    audio_format = args.format
    if audio_format != 'wav':
        print('The current implementation does not support {}'.format(audio_format))
        sys.exit(-1)
    audio_files = glob.glob(os.path.join(wav_dir, '*.{}'.format(audio_format)))
    num_files = len(audio_files)
    if num_files == 0:
        print("no {} found in {}".format(audio_format, wav_dir))
        sys.exit(-1)
    print('# of audio files: {}'.format(len(audio_files)))
    conf_file = args.conf
    if not os.path.exists(conf_file):
        print('{} doest not exisit'.format(conf_file))
    config.read(conf_file)
    print('loading decoder models ...')
    decoder = load_decoder(config)
    total_duration = 0
    for audio_file in audio_files:
        print('processing', audio_file)
        audio_segment = AudioSegment.from_file(audio_file, format=audio_format)
        total_duration += audio_segment.duration_seconds
        # print('wave duration: {}'.format(datetime.timedelta(seconds=audio_segment.duration_seconds)))
        # print('loading wave stream ...')
        wav_stream = open(audio_file, 'rb')
        # print('decoding ...')
        result = decode_wave(wav_stream, decoder)
        print("CMU Sphinx transcribed the file as: \n{}\n".format(result))
    print('total audio duration: {}'.format(datetime.timedelta(seconds=total_duration)))
    decode_time = time.time() - start_time
    decode_time_str = "decode time: {}".format(datetime.timedelta(seconds=decode_time))
    print(decode_time_str)



"""
How to run: 
python pocketsphinx_parellel_decoder.py -i wav/en -c conf/config_en.ini -f wav 
python pocketsphinx_parellel_decoder.py -i wav/ar -c conf/config_ar.ini -f wav 

"""
