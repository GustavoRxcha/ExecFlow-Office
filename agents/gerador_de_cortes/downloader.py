import os
from pytubefix import YouTube
from pytubefix.cli import on_progress

def baixar_video(url: str, pasta_destino: str = "assets") -> str:
    print(f"[*] Iniciando o download do vídeo: {url}")
    
    try:
        # Mudamos o client para ANDROID_VR. Isso muda a forma como o servidor 
        # do YouTube enxerga o nosso script, burlando o bloqueio Web.
        yt = YouTube(url, on_progress_callback=on_progress, client='ANDROID_VR')
        
        print(f"[*] Título encontrado: {yt.title}")
        
        stream = yt.streams.get_highest_resolution()
        
        print("[*] Baixando... (isso pode levar alguns segundos)")
        
        arquivo_baixado = stream.download(output_path=pasta_destino)
        
        print(f"\n[+] Download concluído com sucesso: {arquivo_baixado}")
        return arquivo_baixado
        
    except Exception as e:
        print(f"\n[-] Erro ao baixar o vídeo: {e}")
        return None