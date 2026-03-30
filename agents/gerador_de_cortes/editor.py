import re
import ollama

def analisar_corte(caminho_txt: str) -> list:
    print(f"\n[*] Analisando transcrição com Ollama: {caminho_txt}")
    
    with open(caminho_txt, 'r', encoding='utf-8') as f:
        transcricao = f.read()

    # Prompt instruindo a IA a buscar múltiplos cortes de 60-90s
    prompt = f"""
    Você é um especialista em vídeos curtos virais.
    Encontre os 3 trechos mais engajadores da transcrição abaixo.
    Cada trecho DEVE ter obrigatoriamente entre 60 e 90 segundos de duração.
    Responda APENAS com os tempos de início e fim de cada corte, um por linha, no formato: [INICIO] - [FIM].
    Exemplo:
    45.50 - 110.20
    150.00 - 225.30
    300.10 - 370.40

    Não escreva justificativas, introduções ou qualquer outro texto. Apenas os números.

    Transcrição:
    {transcricao}
    """

    try:
        print("[*] Aguardando decisão do Llama 3.1...")
        # Atualizado para llama3.1
        resposta = ollama.chat(model='llama3.1', messages=[
            {'role': 'user', 'content': prompt}
        ])
        
        texto_resposta = resposta['message']['content'].strip()
        print(f"[*] Resposta bruta do LLM:\n{texto_resposta}")
        
        # Regex para encontrar múltiplos pares de números (ex: 45.50 - 110.20)
        padrao = r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)'
        matches = re.findall(padrao, texto_resposta)
        
        cortes = []
        for inicio_str, fim_str in matches:
            inicio = float(inicio_str)
            fim = float(fim_str)
            
            # Validação: garante que o fim é maior que o início
            if fim > inicio:
                cortes.append((inicio, fim))
        
        if cortes:
            print(f"\n[+] {len(cortes)} cortes capturados com sucesso:")
            for i, (ini, f) in enumerate(cortes, 1):
                duracao = f - ini
                print(f"    Corte {i}: de {ini}s até {f}s (Duração: {duracao:.2f}s)")
            return cortes
        else:
            print("[-] Falha: O LLM não retornou tempos válidos ou fora do formato.")
            return []
            
    except Exception as e:
        print(f"[-] Erro ao comunicar com Ollama: {e}")
        return []