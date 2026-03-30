import os
import ffmpeg

def renderizar_cortes(caminho_video: str, cortes: list, pasta_destino: str = "output") -> list:
    print("\n[*] Preparando os motores do FFmpeg para edição...")
    
    # Pega o nome do vídeo original sem a extensão .mp4
    nome_base = os.path.basename(caminho_video).rsplit('.', 1)[0]
    arquivos_gerados = []
    
    for i, (inicio, fim) in enumerate(cortes, 1):
        arquivo_saida = os.path.join(pasta_destino, f"{nome_base}_corte_{i}.mp4")
        print(f"[*] Processando Corte {i} (De {inicio}s até {fim}s)...")
        
        try:
            # A mágica acontece aqui:
            # 1. ss=inicio e to=fim (Corta o tempo exato)
            # 2. filter('crop', 'ih*9/16', 'ih') (Pega a altura do vídeo e calcula a largura ideal para 9:16, centralizando a imagem)
            (
                ffmpeg
                .input(caminho_video, ss=inicio, to=fim)
                .filter('crop', 'ih*9/16', 'ih') 
                .output(arquivo_saida, vcodec='libx264', acodec='aac', loglevel='error')
                .overwrite_output()
                .run()
            )
            print(f"[+] Corte {i} finalizado com sucesso: {arquivo_saida}")
            arquivos_gerados.append(arquivo_saida)
            
        except Exception as e:
            print(f"[-] Erro ao renderizar o corte {i}: {e}")
            
    return arquivos_gerados