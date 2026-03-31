import os
import shutil
from downloader import baixar_video
from transcriber import transcrever_video
from editor import analisar_corte
from render import renderizar_cortes

# Define o diretório base como a pasta exata onde este arquivo (main.py) está localizado
DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))

def configurar_pastas():
    pastas = ['assets', 'output', 'temp']
    for pasta in pastas:
        os.makedirs(pasta, exist_ok=True)

def limpar_pastas(pastas_para_limpar):
    print("\n--- LIMPANDO ARQUIVOS TEMPORÁRIOS ---")
    for pasta in pastas_para_limpar:
        if os.path.exists(pasta):
            for arquivo in os.listdir(pasta):
                caminho_arquivo = os.path.join(pasta, arquivo)
                try:
                    if os.path.isfile(caminho_arquivo) or os.path.islink(caminho_arquivo):
                        os.unlink(caminho_arquivo)
                    elif os.path.isdir(caminho_arquivo):
                        shutil.rmtree(caminho_arquivo)
                    print(f"[*] Removido: {arquivo}")
                except Exception as e:
                    print(f"[-] Erro ao deletar {caminho_arquivo}: {e}")
    print("[+] Limpeza concluída. Apenas a pasta 'output' foi preservada.")

def main():
    # Força todo o fluxo de trabalho a acontecer estritamente dentro de 'gerador_de_cortes'
    os.chdir(DIRETORIO_BASE)
    
    print("=== GERADOR DE CORTES AUTOMATIZADO ===")
    configurar_pastas()
    
    url_video = input("\nInsira o link do vídeo do YouTube: ")
    if not url_video: return

    # FASE 1: Download
    print("\n--- FASE 1: DOWNLOAD ---")
    caminho_video = baixar_video(url_video)
    if not caminho_video: return

    # FASE 2: Transcrição
    print("\n--- FASE 2: TRANSCRIÇÃO ---")
    caminho_txt = transcrever_video(caminho_video)
    if not caminho_txt: return

    # FASE 3: Fatiamento
    print("\n--- FASE 3: INTELIGÊNCIA DO CORTE ---")
    cortes = analisar_corte(caminho_txt)
    if not cortes: 
        print("\n[-] Nenhum corte capturado. Encerrando.")
        return

    # FASE 4: Renderização e Crop
    print("\n--- FASE 4: RENDERIZAÇÃO (FFMPEG) ---")
    arquivos_finais = renderizar_cortes(caminho_video, cortes)
    
    if arquivos_finais:
        print(f"\n[!] PROCESSO CONCLUÍDO! {len(arquivos_finais)} cortes gerados.")
        limpar_pastas(['assets', 'temp'])
        
        # Mostra o caminho absoluto no final para confirmar que foi para o lugar certo
        caminho_output = os.path.join(DIRETORIO_BASE, 'output')
        print(f"\nPronto! Verifique a pasta '{caminho_output}' para os arquivos finais.")

if __name__ == "__main__":
    main()