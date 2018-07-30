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
import os
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


def load_default_decoder():
    # Create a decoder with default model
    pocketsphinx_config = DefaultConfig()
    model_path = get_model_path()
    pocketsphinx_config.set_string('-hmm', os.path.join(model_path, 'en-us'))
    pocketsphinx_config.set_string('-lm', os.path.join(model_path, 'en-us.lm.bin'))
    pocketsphinx_config.set_string('-dict', os.path.join(model_path, 'cmudict-en-us.dict'))
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
parser.add_argument('-i', '--infile', type=str,
                    help='input wave file', required=True)
parser.add_argument('-c', '--conf', type=str, help='configuration file')

if __name__ == '__main__':
    config = configparser.ConfigParser()
    start_time = time.time()
    args = parser.parse_args()
    decoder = None
    if args.conf:
        conf_file = args.conf
        config.read(conf_file)
        decoder = load_decoder(config)
    else:
        decoder = load_default_decoder()
    wav_file = args.infile
    print('processing', wav_file)
    audio_segment = AudioSegment.from_wav(wav_file)
    print('wave duration: {}'.format(datetime.timedelta(seconds=audio_segment.duration_seconds)))
    wav_stream = open(wav_file, 'rb')
    result = decode_wave(wav_stream, decoder)
    decode_time = time.time() - start_time
    decode_time_str = "decode time: {}".format(datetime.timedelta(seconds=decode_time))
    print(decode_time_str)
    print("Sphinx transcribed the file as: \n{}\n".format(result))





