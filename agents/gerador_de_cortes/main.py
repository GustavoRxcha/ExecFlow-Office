import os
from downloader import baixar_video
from transcriber import transcrever_video
from editor import analisar_corte
from render import renderizar_cortes # Importamos o novo módulo

# Garante que o script sempre execute no diretório onde ele está localizado
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def configurar_pastas():
    pastas = ['assets', 'output', 'temp']
    for pasta in pastas:
        os.makedirs(pasta, exist_ok=True)

def main():
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

    # FASE 3: Inteligência do Corte
    print("\n--- FASE 3: INTELIGÊNCIA DO CORTE ---")
    cortes = analisar_corte(caminho_txt)
    if not cortes: 
        print("\n[-] Nenhum corte capturado. Encerrando.")
        return

    # FASE 4: Renderização e Crop
    print("\n--- FASE 4: RENDERIZAÇÃO (FFMPEG) ---")
    arquivos_finais = renderizar_cortes(caminho_video, cortes)
    
    if arquivos_finais:
        print(f"\n[!] PROCESSO CONCLUÍDO! {len(arquivos_finais)} cortes foram gerados.")
        print("Verifique a pasta 'output' para assistir aos resultados.")

if __name__ == "__main__":
    main()