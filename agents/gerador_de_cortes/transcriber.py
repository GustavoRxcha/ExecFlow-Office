import os
from faster_whisper import WhisperModel

def transcrever_video(caminho_video: str, pasta_destino: str = "temp") -> str:
    print(f"\n[*] Iniciando transcrição do arquivo: {caminho_video}")
    print("[*] Carregando o modelo Whisper da OpenAI (isso pode demorar um pouquinho na primeira vez que baixar)...")
    
    # Usamos o modelo 'small' para ser rápido no Mac. 
    # Para testes iniciais é ótimo. Depois podemos testar o 'medium' se precisar de mais precisão.
    modelo = WhisperModel("small", device="cpu", compute_type="int8")
    
    # O word_timestamps=True é o segredo para sabermos o tempo exato para as legendas
    segmentos, info = modelo.transcribe(caminho_video, beam_size=5, word_timestamps=True)
    
    print(f"[*] Idioma detectado: {info.language} (Probabilidade: {info.language_probability})")
    print("[*] Extraindo falas...")
    
    # Vamos salvar a transcrição em um arquivo de texto na pasta temp
    nome_arquivo = os.path.basename(caminho_video).rsplit('.', 1)[0] + ".txt"
    caminho_txt = os.path.join(pasta_destino, nome_arquivo)
    
    with open(caminho_txt, "w", encoding="utf-8") as f:
        for segmento in segmentos:
            # Formata a linha mostrando o segundo inicial, final e o texto
            linha = f"[{segmento.start:.2f}s -> {segmento.end:.2f}s] {segmento.text}"
            print(linha) # Mostra no terminal para você acompanhar
            f.write(linha + "\n")
            
    print(f"\n[+] Transcrição concluída e salva em: {caminho_txt}")
    return caminho_txt