import os
import sys
import wave
import json
from vosk import Model, KaldiRecognizer, SetLogLevel
# import Word
import subprocess
# from detoxify import Detoxify
import pandas as pd
# from dbpunctuator.inference import Inference, InferenceArguments
# from dbpunctuator.utils import DEFAULT_ENGLISH_TAG_PUNCTUATOR_MAP

def audio_to_text(epoch_dict, audio_file):

    if not os.path.exists(audio_file):
        video_path = ('/').join(audio_file.split('/')[:-1]) + '/fullstream.mp4 '
        convert = "ffmpeg -i " + video_path + "-ab 160k -ac 2 -ar 44110 -vn " + audio_file
        subprocess.call(convert)

    SetLogLevel(0)

    model = Model("assets/vosk-model-en-us-0.22")
    print("Audio to text model loaded...")

    audio = audio_file

    sample_rate=16000
    #     model = Model("model_aspire")
    # model = Model("model_english")
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)

    process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                                audio,
                                '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
                                stdout=subprocess.PIPE, shell=True)

    results = []
    result = ""

    # recognize speech using vosk model
    while True:
        data = process.stdout.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            part_result = json.loads(rec.Result())
            # print(part_result)
            results.append(part_result)
            
                    
            if part_result['text'] != '':
                result += part_result['text'] + "\n\n"
    #             temp += r['text'] + ' '

    part_result = json.loads(rec.FinalResult())
    results.append(part_result)

    print("Processing text into epochs...")

    lines = []
    for obj in results:
        if obj['text'] == '':
            continue
        # print("start: " + str(obj['result'][0]['start']) + ". End: " + str(obj['result'][-1]['end']))
        # print(obj['text'])
        lines.append([obj['result'][0]['start'],obj['result'][-1]['end'],obj['text']])

    epoch_text = [[] for x in range(len(epoch_dict))]
    for line in lines:
        for i,j in enumerate(epoch_dict.values()):
            if line[0] > j[0]/500 and line[1] < j[1]/500:
                epoch_text[i].append(line[2])

    print("Creating toxicity reports...")

#     epoch_text = [["It's secure okay he was hurt the timer",
#   'Yeah.,',
#   "It's pretty good i can. It's pretty good.",
#   'Uncountable right now.',
#   'What did you do today?',
#   'Do some research worked on my slides. Okay.',
#   "Would you you could like move that if you want to like, put your back against that and then i'll be able to see you easier.",
#   'Natalie..',
#   "The law in video and everything's being recorded.",
#   'Please.',
#   'He talks.'],
#  ['I made him fun. I had memes oh, really..',
#   'The one name presently to your team.',
#   "I'll probably present it next week.",
#   'But'],
#  ["The worst thing is to be ignorant of your limitations so you just like, go up there and start expounding on things i'm like, oh yeah, we can do everything will be new orleans and we're so cool and amazing and yeah, that's like, you know just so everyone knows, like we know or i",
#   "I know that this there are this isn't like a magic bullet you know what i mean? This there are some drawbacks to these approaches and limitations and whatnot..",
#   'You guys are crazy, i guess it is.',
#   'Remember that?',
#   'What were they like three months ago',
#   'Have to give it to you. So',
#   'Like asleep.',
#   'Yeah like a stone slate..',
#   'T-bone backers.',
#   'Online.',
#   'Jesus you would like it. She was hoping to bring it here but'],
#  ["So here's hoping..",
#   "Where's the play tomorrow??",
#   'Wow.!',
#   "You'll like it.",
#   "You didn't bring it",
#   'A bunch of material.',
#   "I think that's good.",
#   "It's slow and powdery may not have recorded that spit.",
#   'We',
#   'We gotta take all this stuff up.'],
#  ['Haha yeah yeah yeah..']]

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
        if j:
            tox = Detoxify('original').predict(j)
            df = pd.DataFrame(tox)*100
            epoch_text[i].append(df.mean())
        # epoch_text[i] = punctuator_model.punctuation(j)[0]
    
    return epoch_text
    


# from multiprocessing import freeze_support

# if __name__ == '__main__':
#     audio_to_text("empty", "for_now")
    

