import os, sys
from pocketsphinx import DefaultConfig, Decoder
import time
from pydub import AudioSegment
import datetime
import io
import logging
logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)


class MyDecoder:
    ##########################################
    def __init__(self, model_config):
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
        self.decoder_engine = Decoder(pocketsphinx_config)

    def decode_audio(self, audio_file):
        decode_result = {}
        audio_segment = AudioSegment.from_file(audio_file)
        # audio_segment = audio_segment.set_frame_rate(16000)
        # audio_segment = audio_segment.set_channels(1)
        duration = audio_segment.duration_seconds
        conversion_time = 0
        if not audio_file.endswith('.wav'):
            conversion_start_time = time.time()
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
        decode_time_start_time = time.time()
        self.decoder_engine.start_utt()
        while True:
            buf = wav_stream.read(1024)
            if buf:
                self.decoder_engine.process_raw(buf, False, False)
            else:
                break
        self.decoder_engine.end_utt()
        hypothesis = self.decoder_engine.hyp()
        try:
            text = hypothesis.hypstr
        except AttributeError:
            text = ''
        decode_time = time.time() - decode_time_start_time
        decode_result[audio_file] = (duration, decode_time, conversion_time, text)
        return decode_result


