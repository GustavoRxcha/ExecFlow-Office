import os
import ffmpeg

def renderizar_cortes(caminho_video: str, cortes: list, pasta_destino: str = "output") -> list:
    print("\n[*] Preparando os motores do FFmpeg para edição...")
    
    nome_base = os.path.basename(caminho_video).rsplit('.', 1)[0]
    arquivos_gerados = []
    
    for i, (inicio, fim) in enumerate(cortes, 1):
        arquivo_saida = os.path.join(pasta_destino, f"{nome_base}_corte_{i}.mp4")
        print(f"[*] Processando Corte {i} (De {inicio:.2f}s até {fim:.2f}s)...")
        
        try:
            # Carrega o vídeo definindo o ponto de início e fim
            entrada = ffmpeg.input(caminho_video, ss=inicio, to=fim)
            
            # Isola a trilha de vídeo e aplica o crop vertical (9:16)
            video = entrada.video.filter('crop', 'ih*9/16', 'ih')
            
            # Isola a trilha de áudio original (sem aplicar filtros)
            audio = entrada.audio
            
            # Junta o vídeo editado e o áudio original no arquivo de saída
            (
                ffmpeg
                .output(video, audio, arquivo_saida, vcodec='libx264', acodec='aac', loglevel='error')
                .overwrite_output()
                .run()
            )
            print(f"[+] Corte {i} finalizado com sucesso: {arquivo_saida}")
            arquivos_gerados.append(arquivo_saida)
            
        except Exception as e:
            print(f"[-] Erro ao renderizar o corte {i}: {e}")
            
    return arquivos_gerados