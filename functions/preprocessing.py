# If eyestream video exists, then do blink detection. If it does not exist, hide vid component
# If fullstream video exists, make an mp3 file, then do epoch agnostic audio-to-text 
# toxicity would need to be performed in main dashboard app because it's epoch-dependent

import os
import sys
import wave
import json
from vosk import Model, KaldiRecognizer, SetLogLevel
# import Word
import subprocess
from detoxify import Detoxify
import pandas as pd
from dbpunctuator.inference import Inference, InferenceArguments
from dbpunctuator.utils import DEFAULT_ENGLISH_TAG_PUNCTUATOR_MAP

def audio_to_text(epoch_dict, audio_file):

    # if audio file does not exist, create it from the fullstream video

    if not os.path.exists(audio_file):
        video_path = ('/').join(audio_file.split('/')[:-1]) + '/fullstream.mp4 '
        convert = "ffmpeg -i " + video_path + "-ab 160k -ac 2 -ar 44110 -vn " + audio_file
        subprocess.call(convert)

    SetLogLevel(0)

    model = Model("assets/vosk-model-en-us-0.22")
    print("Audio to text model loaded...")

    audio = audio_file

    sample_rate=16000
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)

    process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                                audio,
                                '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
                                stdout=subprocess.PIPE)

    results = []
    result = ""

    # # recognize speech using vosk model
    # while True:
    #     data = process.stdout.read(4000)
    #     if len(data) == 0:
    #         break
    #     if rec.AcceptWaveform(data):
    #         part_result = json.loads(rec.Result())
    #         # print(part_result)
    #         results.append(part_result)
            
                    
    #         if part_result['text'] != '':
    #             result += part_result['text'] + "\n\n"
    # #             temp += r['text'] + ' '

    # part_result = json.loads(rec.FinalResult())
    # results.append(part_result)

    # print("Processing text into epochs...")

    # lines = []
    # for obj in results:
    #     if obj['text'] == '':
    #         continue
    #     # print("start: " + str(obj['result'][0]['start']) + ". End: " + str(obj['result'][-1]['end']))
    #     # print(obj['text'])
    #     lines.append([obj['result'][0]['start'],obj['result'][-1]['end'],obj['text']])

    # epoch_text = [[] for x in range(len(epoch_dict))]
    # for line in lines:
    #     for i,j in enumerate(epoch_dict.values()):
    #         if line[0] > j[0]/500 and line[1] < j[1]/500:
    #             epoch_text[i].append(line[2])

    # print("Creating toxicity reports...")

 # Punctuation inference 
    # args = InferenceArguments(
    #         model_name_or_path="Qishuai/distilbert_punctuator_en",
    #         tokenizer_name="Qishuai/distilbert_punctuator_en",
    #         tag2punctuator=DEFAULT_ENGLISH_TAG_PUNCTUATOR_MAP
    #     )
    # punctuator_model = Inference(inference_args=args, 
    #                             verbose=False)

    # print("OK")
    for i,j in enumerate(epoch_text):
        tox = Detoxify('original').predict(j)
        # epoch_text[i] = punctuator_model.punctuation(j)[0]
        
        df = pd.DataFrame(tox)*100
        epoch_text[i].append(df.mean())

    return epoch_text
    


from multiprocessing import freeze_support

if __name__ == '__main__':
    audio_to_text("empty", "for_now")
    