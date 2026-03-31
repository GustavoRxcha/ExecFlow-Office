import os
import ffmpeg
import textwrap

# --- FUNÇÕES AUXILIARES DE TEMPO (Necessárias para a sincronia) ---
def parse_srt_time(time_str):
    """Transforma o tempo do SRT (00:00:00,000) em segundos matemáticos."""
    h, m, s_ms = time_str.split(':')
    s, ms = s_ms.split(',')
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0

def format_srt_time(seconds):
    """Transforma os segundos de volta para o formato de texto do SRT."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

# --- NOVA FUNÇÃO: DIVISÃO INTELIGENTE DE TEXTO ---
def otimizar_texto_legenda(texto, caracteres_por_linha=30):
    """
    Recebe um texto longo e quebra em linhas curtas.
    Garante no máximo 2 linhas por bloco de legenda.
    Retorna uma lista de blocos de texto otimizados.
    """
    # Remove espaços extras e quebras de linha existentes da IA
    texto_limpo = " ".join(texto.split())
    
    # Quebra o texto em linhas de no máximo X caracteres
    linhas = textwrap.wrap(texto_limpo, width=caracteres_por_linha)
    
    blocos_finais = []
    # Agrupa as linhas em pares (máximo 2 linhas por exibição)
    for i in range(0, len(linhas), 2):
        par_de_linhas = linhas[i:i+2]
        blocos_finais.append("\n".join(par_de_linhas))
        
    return blocos_finais

# --- FUNÇÃO DE GERAÇÃO DE SRT CORRIGIDA ---
def gerar_srt_do_corte(srt_original, srt_novo, inicio_corte, fim_corte):
    """Lê o SRT original, cria um novo, corta, zera o relógio e DIVIDE textos longos."""
    with open(srt_original, 'r', encoding='utf-8') as f:
        conteudo = f.read().strip()
        if not conteudo: return
        blocos = conteudo.split('\n\n')

    novos_blocos_srt = []
    contador_legenda = 1

    for bloco in blocos:
        linhas = bloco.split('\n')
        if len(linhas) >= 3:
            tempos = linhas[1].split(' --> ')
            try:
                inicio_leg = parse_srt_time(tempos[0])
                fim_leg = parse_srt_time(tempos[1])
                # Pega o texto original (pode ter várias linhas da IA)
                texto_original = " ".join(linhas[2:]) 

                # Se a frase aconteceu dentro do tempo deste corte
                if fim_leg > inicio_corte and inicio_leg < fim_corte:
                    
                    # 1. Aplica a Otimização de Texto (Garante max 2 linhas curtas)
                    # Isso pode transformar 1 bloco longo em 2 ou 3 blocos curtos
                    textos_otimizados = otimizar_texto_legenda(texto_original)
                    num_novos_blocos = len(textos_otimizados)
                    
                    # 2. Calcula a duração total e divide entre os novos mini-blocos
                    duracao_total = fim_leg - inicio_leg
                    duracao_por_bloco = duracao_total / num_novos_blocos
                    
                    # 3. Cria as novas entradas SRT sincronizadas
                    for i, texto_curto in enumerate(textos_otimizados):
                        # Recalcula os tempos baseados no início do corte (zerando relógio)
                        tempo_inicio_relativo = max(0, inicio_leg - inicio_corte) + (i * duracao_por_bloco)
                        tempo_fim_relativo = tempo_inicio_relativo + duracao_por_bloco
                        
                        # Formata o novo bloco SRT
                        novo_bloco = (
                            f"{contador_legenda}\n"
                            f"{format_srt_time(tempo_inicio_relativo)} --> {format_srt_time(tempo_fim_relativo)}\n"
                            f"{texto_curto}\n"
                        )
                        novos_blocos_srt.append(novo_bloco)
                        contador_legenda += 1

            except Exception as e:
                print(f"[-] Erro ao processar bloco de legenda: {e}")
                continue

    # Salva o novo arquivo SRT otimizado
    with open(srt_novo, 'w', encoding='utf-8') as f:
        f.write('\n'.join(novos_blocos_srt) + '\n')

# --- FUNÇÃO PRINCIPAL DE RENDERIZAÇÃO ---
def renderizar_cortes(caminho_video: str, cortes: list, pasta_destino: str = "output") -> list:
    print("\n[*] Preparando os motores do FFmpeg para edição com legendas ULTRA-compactas e sincronizadas...")
    
    if not cortes:
        print("[-] Nenhhum corte para renderizar.")
        return []

    nome_base = os.path.basename(caminho_video).rsplit('.', 1)[0]
    caminho_srt_original = os.path.join("temp", f"{nome_base}.srt")
    
    # Verifica se o SRT original existe antes de continuar
    if not os.path.exists(caminho_srt_original):
        print(f"[-] Erro crítico: Arquivo de legenda original não encontrado em {caminho_srt_original}")
        return []

    arquivos_gerados = []
    
    for i, (inicio, fim) in enumerate(cortes, 1):
        arquivo_saida = os.path.join(pasta_destino, f"{nome_base}_corte_{i}.mp4")
        
        # 1. Cria um arquivo de legenda individual, sincronizado E OTIMIZADO (max 2 linhas)
        caminho_srt_corte = os.path.join("temp", f"{nome_base}_corte_{i}.srt")
        gerar_srt_do_corte(caminho_srt_original, caminho_srt_corte, inicio, fim)
        
        # O Windows exige isso para ler o caminho dentro do FFmpeg
        caminho_srt_ffmpeg = caminho_srt_corte.replace('\\', '/').replace(':', '\\:')
        
        print(f"[*] Processando Corte {i} com Legendas Otimizadas (De {inicio:.2f}s até {fim:.2f}s)...")
        
        try:
            entrada = ffmpeg.input(caminho_video, ss=inicio, to=fim)
            
            # --- ESTILO DA LEGENDA ULTRA-COMPACTA ---
            # FontSize=10: TAMANHO PELA METADE (era 20). Pequeno, mas legível em mobile.
            # Outline=1, Shadow=1: Borda e sombra mais finas para fonte pequena.
            # MarginV=20: Mais colada na borda inferior para não cobrir informações.
            # caracteres_por_linha=30 (na função otimizar): Garante linhas curtas.
            estilo_legenda = (
                "FontName=Arial,Bold=1,FontSize=10,"
                "PrimaryColour=&H00FFFF,OutlineColour=&H40000000,"
                "BorderStyle=1,Outline=1,Shadow=1,"
                "Alignment=2,MarginV=20"
            )
            
            video = (
                entrada.video
                .filter('crop', 'ih*9/16', 'ih') # Crop Vertical
                .filter('subtitles', caminho_srt_ffmpeg, force_style=estilo_legenda) # Queima legenda otimizada
            )
            
            audio = entrada.audio
            
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