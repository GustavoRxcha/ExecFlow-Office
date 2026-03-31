import os
import math
from faster_whisper import WhisperModel

def formatar_tempo_srt(segundos: float) -> str:
    """Converte segundos para o formato do SRT (HH:MM:SS,mmm)"""
    horas = math.floor(segundos / 3600)
    minutos = math.floor((segundos % 3600) / 60)
    segs = math.floor(segundos % 60)
    milisegundos = math.floor((segundos % 1) * 1000)
    return f"{horas:02d}:{minutos:02d}:{segs:02d},{milisegundos:03d}"

def transcrever_video(caminho_video: str, pasta_destino: str = "temp") -> str:
    print(f"\n[*] Iniciando transcrição do arquivo: {caminho_video}")
    print("[*] Carregando o modelo Whisper da OpenAI...")
    
    modelo = WhisperModel("small", device="cpu", compute_type="int8")
    segmentos, info = modelo.transcribe(caminho_video, beam_size=5, word_timestamps=True)
    
    nome_arquivo = os.path.basename(caminho_video).rsplit('.', 1)[0]
    caminho_txt = os.path.join(pasta_destino, nome_arquivo + ".txt")
    caminho_srt = os.path.join(pasta_destino, nome_arquivo + ".srt") # Novo arquivo de legenda
    
    print(f"[*] Idioma detectado: {info.language}")
    print("[*] Extraindo falas e gerando legendas...")
    
    # Abrimos os dois arquivos para salvar simultaneamente
    with open(caminho_txt, "w", encoding="utf-8") as f_txt, open(caminho_srt, "w", encoding="utf-8") as f_srt:
        for i, segmento in enumerate(segmentos, start=1):
            # 1. Salva o TXT (usado pelo nosso fatiador matemático)
            linha_txt = f"[{segmento.start:.2f}s -> {segmento.end:.2f}s] {segmento.text}"
            print(linha_txt)
            f_txt.write(linha_txt + "\n")
            
            # 2. Salva o SRT (usado pelo FFmpeg para queimar a legenda na tela)
            inicio_srt = formatar_tempo_srt(segmento.start)
            fim_srt = formatar_tempo_srt(segmento.end)
            f_srt.write(f"{i}\n")
            f_srt.write(f"{inicio_srt} --> {fim_srt}\n")
            f_srt.write(f"{segmento.text.strip()}\n\n")
            
    print(f"\n[+] Transcrição concluída! Textos e Legendas salvos em: {pasta_destino}/")
    return caminho_txt