import os
import warnings
import requests
import json
import re
from datetime import datetime
from langchain_ollama import ChatOllama
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process

# --- Configurações de Sistema ---
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TRACING_ENABLED"] = "true" 
warnings.filterwarnings("ignore")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Pedido(BaseModel):
    mensagem: str

# --- Configuração dos Motores (LLMs) ---
# O llama3.1 é usado tanto para a análise técnica quanto para a redação criativa
llm_analista = ChatOllama(model="llama3.1")
llm_criativo = "ollama/llama3.1"

# ---------------------------------------------------------
# FUNÇÃO DE PESQUISA OTIMIZADA (SERPER.DEV)
# ---------------------------------------------------------
def buscar_no_google(query):
    url = "https://google.serper.dev/search"
    # Força a busca a focar no contexto atualizado e detalhes oficiais
    query_expandida = f"{query} últimas notícias cenário oficial detalhes atuais"
    
    payload = json.dumps({
        "q": query_expandida,
        "gl": "br",
        "hl": "pt-br",
        "num": 8 
    })
    headers = {
        'X-API-KEY': '704f37bf7e3d6521a9b7adbeeccca47e7d6f7459', 
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        resultados = response.json()
        contexto = ""
        for item in resultados.get('organic', []):
            contexto += f"\nFonte: {item['title']}\nConteúdo: {item['snippet']}\n"
        return contexto
    except Exception as e:
        print(f"[!] Erro na pesquisa: {e}")
        return ""

@app.post("/gerar_roteiro")
def gerar_roteiro(pedido: Pedido):
    data_atual = datetime.now().strftime("%d de %B de %Y")
    print(f"\n[!] Ordem recebida: {pedido.mensagem}")

    # 1. Pesquisa e Geração de Briefing de Inteligência
    fatos_brutos = buscar_no_google(pedido.mensagem)
    
    if fatos_brutos:
        print("[!] Analista a gerar Briefing de Contexto...")
        prompt_analise = f"""
        Analise os dados brutos da internet e crie um 'Briefing de Inteligência' para um redator sénior.
        Sua missão é dar PROFUNDIDADE e NARRATIVA ao tema.
        
        REGRAS CRÍTICAS:
        - Liste FATOS (nomes, datas, locais, números).
        - Descreva o CENÁRIO ATUAL (o que está a acontecer agora e porquê).
        - Identifique o SENTIMENTO (expectativa, preocupação, urgência, celebração).
        - Mantenha nomes e termos originais em Português do Brasil.
        
        DADOS BRUTOS:
        {fatos_brutos}
        """
        briefing = llm_analista.invoke(prompt_analise).content
    else:
        briefing = "Sem dados recentes encontrados. Use conhecimento geral vasto e criatividade profissional."

    # 2. Agente Copywriter Estratégico (O Camaleão)
    roteirista = Agent(
        role='Copywriter Estratégico Sênior',
        goal='Criar textos de alto impacto que misturam factos reais com narrativa envolvente.',
        backstory='''Você é o redator principal da ExecFlow. Sua fama vem da capacidade de escrever sobre 
        qualquer assunto — de desportos a finanças — como se fosse um especialista. Você não apenas lista dados, 
        você conecta os factos do briefing com a emoção do momento atual para criar autoridade.''',
        allow_delegation=False,
        llm=llm_criativo,
        verbose=True
    )

    # 3. Tarefa com Regras de Ouro e Instruções de Poda
    tarefa_escrita = Task(
        description=f'''
        DATA ATUAL: {data_atual}
        PEDIDO DO USUÁRIO: "{pedido.mensagem}"
        BRIEFING DE INTELIGÊNCIA: 
        {briefing}
        
        SUA MISSÃO MANDATÓRIA:
        1. Produza EXCLUSIVAMENTE o texto final pronto para uso.
        2. É TERMINANTEMENTE PROIBIDO incluir placeholders como "[insira aqui]" ou frases incompletas.
        3. Se for para redes sociais, use emojis estratégicos e hashtags relevantes.
        4. O texto deve terminar imediatamente após a última frase ou hashtag.
        
        REGRAS DE FORMATAÇÃO (ESTRITAS):
        - RESPONDA APENAS COM O TEXTO DA COPY.
        - Não adicione comentários de ajuda, sugestões de uso ou saudações (ex: "Aqui está seu post").
        - Não inclua frases como "Copie e cole" ou "Espero que ajude".
        ''',
        expected_output='O texto final refinado e completo, sem qualquer comentário ou metadados.',
        agent=roteirista
    )

    # 4. Execução da Crew
    print("[!] A redigir copy profissional com base no contexto...")
    equipe = Crew(
        agents=[roteirista], 
        tasks=[tarefa_escrita], 
        process=Process.sequential,
        verbose=True
    )
    
    resultado_bruto = str(equipe.kickoff())

    # --- SISTEMA DE PODA DE COMENTÁRIOS (Lógica Python) ---
    # 1. Quebra o texto em linhas para analisar o final da resposta
    linhas = resultado_bruto.split('\n')
    resultado_final = []
    
    for linha in linhas:
        # Se encontrarmos frases típicas de "ajuda" do assistente, paramos de processar
        if re.search(r'^(Se precisar|Aqui está|Espero que|Copie e cole|Este texto|Para publicar|Pode usar)', linha, re.IGNORECASE):
            break
        resultado_final.append(linha)

    # 2. Reconstroi o texto e limpa resíduos de Markdown (** ou aspas de bloco)
    resultado_limpo = "\n".join(resultado_final).strip()
    resultado_limpo = resultado_limpo.replace("**", "") # Remove negritos que podem quebrar a UI do Godot
    resultado_limpo = re.sub(r'^\s*["\']|["\']\s*$', '', resultado_limpo) # Remove aspas globais

    print("[!] Processo concluído. Resposta limpa enviada ao Godot.")
    return {"resposta": resultado_limpo}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)