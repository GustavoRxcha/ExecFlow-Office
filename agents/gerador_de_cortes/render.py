import os
import ffmpeg
import platform

# --- CONFIGURAÇÃO DE AMBIENTE (WINDOWS/MAC) ---
def configurar_ffmpeg():
    sistema = platform.system()
    
    if sistema == "Windows":
        # Localiza a pasta /bin dentro do diretório deste script (render.py)
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_bin_path = os.path.join(diretorio_atual, "bin")
        
        if os.path.exists(ffmpeg_bin_path):
            # Adiciona a pasta bin ao PATH temporário da execução
            # os.pathsep é o separador ';' no Windows e ':' no Mac
            os.environ["PATH"] += os.pathsep + ffmpeg_bin_path
            print(f"[*] Windows: Usando FFmpeg local em: {ffmpeg_bin_path}")
        else:
            print("[!] Aviso: Pasta /bin não encontrada no Windows. Tentando FFmpeg global...")
    else:
        print(f"[*] {sistema}: Usando configuração nativa do sistema.")

# Executa a configuração ao importar o módulo
configurar_ffmpeg()

def renderizar_cortes(caminho_video: str, cortes: list, pasta_destino: str = "output") -> list:
    print("\n[*] Preparando os motores do FFmpeg para edição...")
    
    # Garante que a pasta de destino exista
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f"[*] Pasta '{pasta_destino}' criada com sucesso.")
    
    # Pega o nome do vídeo original sem a extensão
    nome_base = os.path.basename(caminho_video).rsplit('.', 1)[0]
    arquivos_gerados = []
    
    for i, (inicio, fim) in enumerate(cortes, 1):
        arquivo_saida = os.path.join(pasta_destino, f"{nome_base}_corte_{i}.mp4")
        duracao = fim - inicio
        
        print(f"[*] Processando Corte {i} ({duracao}s)...")
        
        try:
            # A mágica acontece aqui:
            # 1. ss=inicio e t=duracao (Corta o tempo exato)
            # 2. filter('crop', 'ih*9/16', 'ih') (Centraliza para 9:16 vertical)
            (
                ffmpeg
                .input(caminho_video, ss=inicio, t=duracao)
                .filter('crop', 'ih*9/16', 'ih') 
                .output(
                    arquivo_saida, 
                    vcodec='libx264', 
                    acodec='aac', 
                    loglevel='error',
                    pix_fmt='yuv420p' # Garante compatibilidade com players de celular
                )
                .overwrite_output()
                .run()
            )
            print(f"[+] Corte {i} finalizado: {arquivo_saida}")
            arquivos_gerados.append(arquivo_saida)
            
        except Exception as e:
            print(f"[-] Erro ao renderizar o corte {i}: {e}")
            
    return arquivos_gerados