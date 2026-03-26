using Godot;
using System;
using System.Text;
using System.Collections.Generic;
using System.Text.Json;

public partial class CerebroMestre : Node
{
	// Este dicionário mapeia o nome do setor para a URL da API específica
	// Você deve adicionar novas linhas aqui conforme criar novos gestores
	private Dictionary<string, string> _setores = new Dictionary<string, string>
	{
		{ "Copy", "http://127.0.0.1:8000/gerar_roteiro" },
		// Exemplo de futuro gestor: { "TI", "http://127.0.0.1:8001/suporte" }
	};

	public void EnviarOrdem(string setor, string mensagem, Action<string> aoReceberResposta)
	{
		if (!_setores.ContainsKey(setor))
		{
			GD.PrintErr($"Erro: Setor '{setor}' não configurado no CerebroMestre.");
			return;
		}

		// Cria um nó de requisição HTTP temporário
		HttpRequest http = new HttpRequest();
		AddChild(http);
		
		// Configura o que acontece quando a resposta chegar
		http.RequestCompleted += (long result, long responseCode, string[] headers, byte[] body) => 
		{
			if (responseCode == 200)
			{
				string responseText = Encoding.UTF8.GetString(body);
				// Usamos a classe Json do Godot para ler a resposta da sua API Python
				var json = Json.ParseString(responseText).AsGodotDictionary();
				aoReceberResposta?.Invoke(json["resposta"].ToString());
			}
			else
			{
				aoReceberResposta?.Invoke("Erro: Não foi possível contatar o Gestor.");
			}
			http.QueueFree(); // Deleta o nó HTTP para não pesar a memória
		};

		string url = _setores[setor];
		// Cria o JSON para enviar ao Python: {"mensagem": "seu texto"}
		string payload = JsonSerializer.Serialize(new { mensagem = mensagem });
		string[] headerArr = { "Content-Type: application/json" };

		http.Request(url, headerArr, HttpClient.Method.Post, payload);
	}
}
