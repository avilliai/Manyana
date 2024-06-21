# -*- coding:utf-8 -*-
import asyncio
import datetime
import os
from asyncio import sleep

import httpx
import librosa
import soundfile
from scipy.io.wavfile import write


from .mel_processing import spectrogram_torch

from .text import text_to_sequence, _clean_text
from .models import SynthesizerTrn
from . import utils
from . import commons
import sys
import re
from torch import no_grad, LongTensor
import logging



logging.getLogger('numba').setLevel(logging.WARNING)


def ex_print(text, escape=False):
    if escape:
        print(text.encode('unicode_escape').decode())
    else:
        print(text)


def get_text(text, hps, cleaned=False):
    if cleaned:
        text_norm = text_to_sequence(text, hps.symbols, [])
    else:
        text_norm = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm


def ask_if_continue():
    while True:
        answer = input('Continue? (y/n): ')
        if answer == 'y':
            break
        elif answer == 'n':
            sys.exit(0)


def print_speakers(speakers, escape=False):
    print('ID\tSpeaker')
    for id, name in enumerate(speakers):
        ex_print(str(id) + '\t' + name, escape)


def get_speaker_id(message):
    '''speaker_id = input(message)
    try:
        speaker_id = int(speaker_id)
    except:
        print(str(speaker_id) + ' is not a valid ID!')
        sys.exit(1)
    return speaker_id'''
    return 0


def get_label_value(text, label, default, warning_name='value'):
    value = re.search(rf'\[{label}=(.+?)\]', text)
    if value:
        try:
            text = re.sub(rf'\[{label}=(.+?)\]', '', text, 1)
            value = float(value.group(1))
        except:
            print(f'Invalid {warning_name}!')
            sys.exit(1)
    else:
        value = default
    return value, text


def get_label(text, label):
    if f'[{label}]' in text:
        return True, text.replace(f'[{label}]', '')
    else:
        return False, text

async def vG(tex,out,speakerID=2,modelSelect=['vits/voiceModel/nene/1374_epochsm.pth','vits/voiceModel/nene/config.json'] ):
    if len(tex)>150:

        tex='[JA]長すぎるああ、こんなに長い声..... んもう~[JA]'
        speakerID=0
    #if modelSelect == ['voiceModel/amm/amamiyam.pth','voiceModel/amm/config.json']:
        #tex=tex.replace('[JA]','')
    text=tex
    out_path=out

    if '--escape' in sys.argv:
        escape = True
    else:
        escape = False
    if modelSelect[0].startswith("vits/"):

        model=modelSelect[0]
        config=modelSelect[1]
    else:
        model = modelSelect[0]
        config = modelSelect[1]

    hps_ms = utils.get_hparams_from_file(config)
    n_speakers = hps_ms.data.n_speakers if 'n_speakers' in hps_ms.data.keys() else 0
    n_symbols = len(hps_ms.symbols) if 'symbols' in hps_ms.keys() else 0
    speakers = hps_ms.speakers if 'speakers' in hps_ms.keys() else ['0']
    use_f0 = hps_ms.data.use_f0 if 'use_f0' in hps_ms.data.keys() else False
    emotion_embedding = hps_ms.data.emotion_embedding if 'emotion_embedding' in hps_ms.data.keys() else False

    net_g_ms = SynthesizerTrn(
        n_symbols,
        hps_ms.data.filter_length // 2 + 1,
        hps_ms.train.segment_size // hps_ms.data.hop_length,
        n_speakers=n_speakers,
        emotion_embedding=emotion_embedding,
        **hps_ms.model)
    _ = net_g_ms.eval()
    utils.load_checkpoint(model, net_g_ms)



    if text == '[ADVANCED]':
        text = input('Raw text:')
        print('Cleaned text is:')
        ex_print(_clean_text(
            text, hps_ms.data.text_cleaners), escape)


    length_scale, text = get_label_value(
        text, 'LENGTH', 1.16, 'length scale')
    noise_scale, text = get_label_value(
        text, 'NOISE', 0.667, 'noise scale')
    noise_scale_w, text = get_label_value(
        text, 'NOISEW', 0.7, 'deviation of noise')
    cleaned, text = get_label(text, 'CLEANED')



    stn_tst = get_text(text, hps_ms, cleaned=cleaned)

    #print_speakers(speakers, escape)


    speaker_id = int(speakerID)

    with no_grad():
        x_tst = stn_tst.unsqueeze(0)
        x_tst_lengths = LongTensor([stn_tst.size(0)])
        sid = LongTensor([speaker_id])
        audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale,
                               noise_scale_w=noise_scale_w, length_scale=length_scale)[0][
            0, 0].data.cpu().float().numpy()



    write(out_path, hps_ms.data.sampling_rate, audio)#将生成的语音文件写入本地
    await change_sample_rate(out_path)
async def change_sample_rate(path,new_sample_rate=44100):
    #wavfile = path  # 提取音频文件名，如“1.wav"
    # new_file_name = wavfile.split('.')[0] + '_8k.wav'      #此行代码可用于对转换后的文件进行重命名（如有需要）

    signal, sr = librosa.load(path, sr=None)  # 调用librosa载入音频

    new_signal = librosa.resample(signal, orig_sr=sr, target_sr=new_sample_rate)  # 调用librosa进行音频采样率转换

    new_path = path # 指定输出音频的路径，音频文件与原音频同名
    # new_path = os.path.join(new_dir_path, new_file_name)      #若需要改名则启用此行代码
    #print("?")
    #print(new_path)

    # librosa.output.write_wav(new_path, new_signal , new_sample_rate)      #因版本问题，此方法可能用不了
    soundfile.write(new_path, new_signal, new_sample_rate)


def voice_conversion(sourcepath,speaker=0):
    if '--escape' in sys.argv:
        escape = True
    else:
        escape = False
    afd=['voiceModel/nene/1374_epochsm.pth', 'voiceModel/nene/config.json']
    model = afd[0]
    config = afd[1]

    hps_ms = utils.get_hparams_from_file(config)
    n_speakers = hps_ms.data.n_speakers if 'n_speakers' in hps_ms.data.keys() else 0
    n_symbols = len(hps_ms.symbols) if 'symbols' in hps_ms.keys() else 0
    speakers = hps_ms.speakers if 'speakers' in hps_ms.keys() else ['0']
    use_f0 = hps_ms.data.use_f0 if 'use_f0' in hps_ms.data.keys() else False
    emotion_embedding = hps_ms.data.emotion_embedding if 'emotion_embedding' in hps_ms.data.keys() else False

    net_g_ms = SynthesizerTrn(
        n_symbols,
        hps_ms.data.filter_length // 2 + 1,
        hps_ms.train.segment_size // hps_ms.data.hop_length,
        n_speakers=n_speakers,
        emotion_embedding=emotion_embedding,
        **hps_ms.model)
    _ = net_g_ms.eval()
    utils.load_checkpoint(model, net_g_ms)
    audio_path = sourcepath
    print_speakers(speakers)
    audio = utils.load_audio_to_torch(
        audio_path, hps_ms.data.sampling_rate)

    originnal_id = 0
    target_id = 0
    out_path = 'wa.wav'

    y = audio.unsqueeze(0)

    spec = spectrogram_torch(y, hps_ms.data.filter_length,
                             hps_ms.data.sampling_rate, hps_ms.data.hop_length, hps_ms.data.win_length,
                             center=False)
    spec_lengths = LongTensor([spec.size(-1)])
    sid_src = LongTensor([originnal_id])

    with no_grad():
        sid_tgt = LongTensor([target_id])
        audio = net_g_ms.voice_conversion(spec, spec_lengths, sid_src=sid_src, sid_tgt=sid_tgt)[
            0][0, 0].data.cpu().float().numpy()
    write(out_path, hps_ms.data.sampling_rate, audio)
    print('Successfully saved!')
async def ttsOnline(txt):
    url='https://api.oick.cn/txt/apiz.php'
    data={"text":txt,"spd":6}
    async with httpx.AsyncClient(timeout=100) as client:
        r = await client.get(url,params=data)
        with open('song.mp3', 'wb') as f:
            f.write(r.content)
        voice_conversion("song.mp3")
        #return url
if __name__ == '__main__':
    #voice_conversion("plugins/voices/sing/rest.wav")
    asyncio.run(vG('[JA]先生,ちょっとお時間..いただけますか1?[JA]', '2.wav',0,["voiceModel/bolv.pth","voiceModel/config.json"]))
    print("任务1")
