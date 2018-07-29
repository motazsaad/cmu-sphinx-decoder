from argparse import ArgumentParser

import datetime
import sys
import argparse

import speech_recognition as sr

"""
This decoder is based on CMU Sphinx (works offline) engine provided by speech_recognition python package. 
url: https://pypi.org/project/SpeechRecognition/ 
to install: 
pip install SpeechRecognition
"""

parser = argparse.ArgumentParser(description='This decoder is based CMU Sphinx (works offline) engine provided by '
                                             'speech_recognition python package.')  # type: ArgumentParser
parser.add_argument('-i', '--infile', type=str,
                    help='input wave file', required=True)
parser.add_argument('-c', '--conf', type=str, help='configuration file')


if __name__ == '__main__':
    args = parser.parse_args()
    wave = args.infile
    r = sr.Recognizer()
    try:
        with sr.AudioFile(wave) as source:
            audio = r.record(source)  # read the entire audio file
            duration = source.DURATION
            print("audio length: {}".format(datetime.timedelta(seconds=duration)))
            # recognize speech using Sphinx
            try:
                print("transcribing the file: {}".format(wave))
                text = r.recognize_sphinx(audio_data=audio)
                print("Sphinx transcribed the file as: \n{}\n".format(text))
            except sr.UnknownValueError as error:
                print("ASR could not understand audio")
                text = "error: ASR system could not understand audio"
                print("ASR error: {0}".format(error))
            except sr.RequestError as error:
                print("ASR error: {0}".format(error))
            except BaseException as error:
                print("ASR error: {0}".format(error))
    except BaseException as e:
        print("ASR error: {0}".format(error))


