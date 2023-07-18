# -*- coding:utf-8 -*-
import asyncio
import datetime
from asyncio import sleep

from scipy.io.wavfile import write


from mel_processing import spectrogram_torch
from plugins.RandomStr import random_str
from text import text_to_sequence, _clean_text
from models import SynthesizerTrn
import utils
import commons
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

async def voiceGenerate(tex,out,speakerID=0,modelSelect=['voiceModel/amm/amamiyam.pth','voiceModel/amm/config.json']):
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

    model=modelSelect[0]
    config=modelSelect[1]

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
        text, 'LENGTH', 1.1, 'length scale')
    noise_scale, text = get_label_value(
        text, 'NOISE', 0.667, 'noise scale')
    noise_scale_w, text = get_label_value(
        text, 'NOISEW', 0.8, 'deviation of noise')
    cleaned, text = get_label(text, 'CLEANED')



    stn_tst = get_text(text, hps_ms, cleaned=cleaned)

    #print_speakers(speakers, escape)

    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(time + '| 正在使用语音模型：'+str(speakerID)+' ......生成中'+'  |  文本：'+str(tex))
    speaker_id = int(speakerID)

    with no_grad():
        x_tst = stn_tst.unsqueeze(0)
        x_tst_lengths = LongTensor([stn_tst.size(0)])
        sid = LongTensor([speaker_id])
        audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale,
                               noise_scale_w=noise_scale_w, length_scale=length_scale)[0][
            0, 0].data.cpu().float().numpy()



    write(out_path, hps_ms.data.sampling_rate, audio)#将生成的语音文件写入本地

    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(time + '| Successfully saved!')



def voice_conversion(sourcepath,speaker=0):
    if '--escape' in sys.argv:
        escape = True
    else:
        escape = False

    model = 'voiceModel\\1374_epochsm.pth'#input('Path of a VITS model: ')
    config ='voiceModel\\config.json'#input('Path of a config file: ')

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
    audio = utils.load_audio_to_torch(
        audio_path, hps_ms.data.sampling_rate)

    originnal_id = speaker
    target_id = 3
    out_path = 'plugins\\voices\\sing\\out.wav'

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
    return out_path


if __name__ == '__main__':
    #voice_conversion("plugins/voices/sing/rest.wav")

    print("任务1")
    asyncio.run(voiceGenerate('[JA]先生,ちょっとお時間..いただけますか1?[JA]', 'voices/'+random_str()+'1.wav'))
    print("任务1")
    asyncio.run(voiceGenerate('[JA]先生,ちょっとお時間..いただけますか2?[JA]', 'voices/'+random_str()+'1.wav'))
    print("任务1")
    asyncio.run(voiceGenerate('[JA]先生,ちょっとお時間..いただけますか3?[JA]', 'voices/'+random_str()+'1.wav'))



    '''async def voiceG():
        await voiceGenerate('[JA]先生,ちょっとお時間..いただけますか?[JA]','voiceModel/1.wav')
    asyncio.run(voiceG())'''

    '''ranpath = random_str()
    Path=sys.argv[0][:-23]
    print(Path)
    out = Path+'PythonPlugins\\plugins\\voices\\' + ranpath + '.wav'
    tex = '[JA]' + translate('测试语音.....') + '[JA]'
    voiceGenerate(tex, out)'''
    '''if '--escape' in sys.argv:
        escape = True
    else:
        escape = False

    model = input('Path of a VITS model: ')
    config = input('Path of a config file: ')

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

    def voice_conversion():
        audio_path = input('Path of an audio file to convert:\n')
        print_speakers(speakers)
        audio = utils.load_audio_to_torch(
            audio_path, hps_ms.data.sampling_rate)

        originnal_id = get_speaker_id('Original speaker ID: ')
        target_id = get_speaker_id('Target speaker ID: ')
        out_path = input('Path to save: ')

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
        return audio, out_path

    if n_symbols != 0:
        if not emotion_embedding:
            while True:
                choice = input('TTS or VC? (t/v):')
                if choice == 't':
                    text = input('Text to read: ')
                    if text == '[ADVANCED]':
                        text = input('Raw text:')
                        print('Cleaned text is:')
                        ex_print(_clean_text(
                            text, hps_ms.data.text_cleaners), escape)
                        continue

                    length_scale, text = get_label_value(
                        text, 'LENGTH', 1, 'length scale')
                    noise_scale, text = get_label_value(
                        text, 'NOISE', 0.667, 'noise scale')
                    noise_scale_w, text = get_label_value(
                        text, 'NOISEW', 0.8, 'deviation of noise')
                    cleaned, text = get_label(text, 'CLEANED')

                    stn_tst = get_text(text, hps_ms, cleaned=cleaned)

                    print_speakers(speakers, escape)
                    speaker_id = get_speaker_id('Speaker ID: ')
                    out_path = input('Path to save: ')

                    with no_grad():
                        x_tst = stn_tst.unsqueeze(0)
                        x_tst_lengths = LongTensor([stn_tst.size(0)])
                        sid = LongTensor([speaker_id])
                        audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale,
                                               noise_scale_w=noise_scale_w, length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()

                elif choice == 'v':
                    audio, out_path = voice_conversion()

                write(out_path, hps_ms.data.sampling_rate, audio)
                print('Successfully saved!')
                ask_if_continue()
        else:
            import os
            import librosa
            import numpy as np
            from torch import FloatTensor
            import audonnx
            w2v2_folder = input('Path of a w2v2 dimensional emotion model: ')
            w2v2_model = audonnx.load(os.path.dirname(w2v2_folder))
            while True:
                choice = input('TTS or VC? (t/v):')
                if choice == 't':
                    text = input('Text to read: ')
                    if text == '[ADVANCED]':
                        text = input('Raw text:')
                        print('Cleaned text is:')
                        ex_print(_clean_text(
                            text, hps_ms.data.text_cleaners), escape)
                        continue

                    length_scale, text = get_label_value(
                        text, 'LENGTH', 1, 'length scale')
                    noise_scale, text = get_label_value(
                        text, 'NOISE', 0.667, 'noise scale')
                    noise_scale_w, text = get_label_value(
                        text, 'NOISEW', 0.8, 'deviation of noise')
                    cleaned, text = get_label(text, 'CLEANED')

                    stn_tst = get_text(text, hps_ms, cleaned=cleaned)

                    print_speakers(speakers, escape)
                    speaker_id = get_speaker_id('Speaker ID: ')

                    emotion_reference = input('Path of an emotion reference: ')
                    if emotion_reference.endswith('.npy'):
                        emotion = np.load(emotion_reference)
                        emotion = FloatTensor(emotion).unsqueeze(0)
                    else:
                        audio16000, sampling_rate = librosa.load(
                            emotion_reference, sr=16000, mono=True)
                        emotion = w2v2_model(audio16000, sampling_rate)[
                            'hidden_states']
                        emotion_reference = re.sub(
                            r'\..*$', '', emotion_reference)
                        np.save(emotion_reference, emotion.squeeze(0))
                        emotion = FloatTensor(emotion)

                    out_path = input('Path to save: ')

                    with no_grad():
                        x_tst = stn_tst.unsqueeze(0)
                        x_tst_lengths = LongTensor([stn_tst.size(0)])
                        sid = LongTensor([speaker_id])
                        audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale, noise_scale_w=noise_scale_w,
                                               length_scale=length_scale, emotion_embedding=emotion)[0][0, 0].data.cpu().float().numpy()

                elif choice == 'v':
                    audio, out_path = voice_conversion()

                write(out_path, hps_ms.data.sampling_rate, audio)
                print('Successfully saved!')
                ask_if_continue()
    else:
        model = input('Path of a hubert-soft model: ')
        from hubert_model import hubert_soft
        hubert = hubert_soft(model)

        while True:
            audio_path = input('Path of an audio file to convert:\n')

            if audio_path != '[VC]':
                import librosa
                if use_f0:
                    audio, sampling_rate = librosa.load(
                        audio_path, sr=hps_ms.data.sampling_rate, mono=True)
                    audio16000 = librosa.resample(
                        audio, orig_sr=sampling_rate, target_sr=16000)
                else:
                    audio16000, sampling_rate = librosa.load(
                        audio_path, sr=16000, mono=True)

                target_id = get_speaker_id('Target speaker ID: ')
                out_path = input('Path to save: ')
                length_scale, out_path = get_label_value(
                    out_path, 'LENGTH', 1, 'length scale')
                noise_scale, out_path = get_label_value(
                    out_path, 'NOISE', 0.1, 'noise scale')
                noise_scale_w, out_path = get_label_value(
                    out_path, 'NOISEW', 0.1, 'deviation of noise')

                from torch import inference_mode, FloatTensor
                import numpy as np
                with inference_mode():
                    units = hubert.units(FloatTensor(audio16000).unsqueeze(
                        0).unsqueeze(0)).squeeze(0).numpy()
                    if use_f0:
                        f0_scale, out_path = get_label_value(
                            out_path, 'F0', 1, 'f0 scale')
                        f0 = librosa.pyin(audio, sr=sampling_rate,
                                          fmin=librosa.note_to_hz('C0'),
                                          fmax=librosa.note_to_hz('C7'),
                                          frame_length=1780)[0]
                        target_length = len(units[:, 0])
                        f0 = np.nan_to_num(np.interp(np.arange(0, len(f0)*target_length, len(f0))/target_length,
                                                     np.arange(0, len(f0)), f0)) * f0_scale
                        units[:, 0] = f0 / 10

                stn_tst = FloatTensor(units)
                with no_grad():
                    x_tst = stn_tst.unsqueeze(0)
                    x_tst_lengths = LongTensor([stn_tst.size(0)])
                    sid = LongTensor([target_id])
                    audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale,
                                           noise_scale_w=noise_scale_w, length_scale=length_scale)[0][0, 0].data.float().numpy()

            else:
                audio, out_path = voice_conversion()

            write(out_path, hps_ms.data.sampling_rate, audio)
            print('Successfully saved!')
            ask_if_continue()'''
