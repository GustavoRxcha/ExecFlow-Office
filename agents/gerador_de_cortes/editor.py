import re

def analisar_corte(caminho_txt: str) -> list:
    print(f"\n[*] Iniciando fatiamento sequencial do arquivo: {caminho_txt}")
    
    linhas_tempo = []
    # Expressão regular para capturar os tempos do arquivo txt gerado pelo Whisper
    # Exemplo alvo: [20.08s -> 28.24s]
    padrao = r'\[([\d\.]+)s\s*->\s*([\d\.]+)s\]'
    
    try:
        with open(caminho_txt, 'r', encoding='utf-8') as f:
            for linha in f:
                match = re.search(padrao, linha)
                if match:
                    inicio = float(match.group(1))
                    fim = float(match.group(2))
                    linhas_tempo.append((inicio, fim))
    except Exception as e:
        print(f"[-] Erro ao ler o arquivo de transcrição: {e}")
        return []

    if not linhas_tempo:
        print("[-] Falha: Não foi possível extrair a minutagem do texto.")
        return []

    cortes = []
    target_duration = 90.0 # Alvo de 1 minuto e 30 segundos
    
    inicio_corte = linhas_tempo[0][0]
    
    for i in range(len(linhas_tempo)):
        fim_atual = linhas_tempo[i][1]
        duracao_atual = fim_atual - inicio_corte
        
        # Se a frase atual fez o bloco bater/passar de 90s, ou se é a última frase do vídeo
        if duracao_atual >= target_duration or i == len(linhas_tempo) - 1:
            cortes.append((inicio_corte, fim_atual))
            
            # Se ainda tem frases pela frente, o próximo corte começa na próxima frase
            if i + 1 < len(linhas_tempo):
                inicio_corte = linhas_tempo[i+1][0]

    # Filtro de sanidade: Remove restos de vídeo no final que tenham menos de 45 segundos
    cortes_filtrados = [c for c in cortes if (c[1] - c[0]) >= 45.0]
    
    if cortes_filtrados:
        print(f"\n[+] Sucesso! O vídeo foi fatiado em {len(cortes_filtrados)} cortes limpos:")
        for i, (ini, f) in enumerate(cortes_filtrados, 1):
            duracao = f - ini
            print(f"    Corte {i}: de {ini:.2f}s até {f:.2f}s (Duração: {duracao:.2f}s)")
        return cortes_filtrados
    else:
        print("[-] Falha: O vídeo é muito curto para gerar cortes com esse tamanho.")
        return []