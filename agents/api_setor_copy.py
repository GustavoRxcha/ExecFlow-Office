from fastapi import FastAPI
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama

app = FastAPI()

# Modelo do dado que o Godot vai enviar
class Pedido(BaseModel):
    mensagem: str

# Inicia o motor local
llm_local = Ollama(model="llama3")

@app.post("/gerar_roteiro")
def gerar_roteiro(pedido: Pedido):
    print(f"Recebido do Godot: {pedido.mensagem}")
    
    # 1. O Gestor
    gestor = Agent(
        role='Gestor de Projetos',
        goal='Analisar o pedido e coordenar o roteirista para entregar o melhor resultado.',
        backstory='Você é um gestor prático e direto da ExecFlow. Você recebe ordens e garante que a equipe execute com perfeição.',
        allow_delegation=True,
        llm=llm_local
    )

    # 2. O Roteirista
    roteirista = Agent(
        role='Roteirista e Redator',
        goal='Escrever textos engajadores, criativos e profissionais.',
        backstory='Você é o redator principal da ExecFlow. Você transforma ideias brutas em textos polidos e bem estruturados.',
        allow_delegation=False,
        llm=llm_local
    )

    # 3. A Tarefa que veio do seu jogo
    tarefa = Task(
        description=f'O usuário pediu: "{pedido.mensagem}". Crie o texto solicitado.',
        expected_output='O texto final, pronto para leitura.',
        agent=gestor
    )

    # 4. Execução
    equipe = Crew(agents=[gestor, roteirista], tasks=[tarefa], process=Process.sequential)
    resultado = equipe.kickoff()
    
    # Devolve o resultado para o Godot
    return {"resposta": resultado}