import ollama

print("Conectando ao Ollama local...")

resposta = ollama.chat(model='llama3', messages=[
    {
        'role': 'user',
        'content': 'Olá! Você é o cérebro do meu novo projeto. Responda em português com apenas uma frase curta para testarmos a conexão.',
    },
])

print("\nResposta do Cérebro:")
print(resposta['message']['content'])