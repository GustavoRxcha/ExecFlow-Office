using Godot;
using System;
using System.Text;
using System.Collections.Generic;
using System.Text.Json;

public partial class CerebroMestre : Node
{
	// Dicionário que mapeia o nome do setor para a URL da API específica
	private Dictionary<string, string> _setores = new Dictionary<string, string>
	{
		{ "Copy", "http://127.0.0.1:8000/gerar_roteiro" },
	};

	public void EnviarOrdem(string setor, string mensagem, Callable aoReceberResposta)
	{
		if (!_setores.ContainsKey(setor))
		{
			GD.PrintErr($"Erro: Setor '{setor}' não configurado no CerebroMestre.");
			return;
		}

		// Cria um nó de requisição HTTP temporário
		HttpRequest http = new HttpRequest();
		AddChild(http);
		
		// Configura o evento de resposta
		http.RequestCompleted += (long result, long responseCode, string[] headers, byte[] body) => 
		{
			if (responseCode == 200)
			{
				string responseText = Encoding.UTF8.GetString(body);
				var json = Json.ParseString(responseText).AsGodotDictionary();
				
				// Correção do Erro CS0023: 
				// Call() já lida internamente com a validação da função no GDScript
				aoReceberResposta.Call(json["resposta"].ToString());
			}
			else
			{
				aoReceberResposta.Call("Erro: Não foi possível contatar o Gestor.");
			}
			
			http.QueueFree(); 
		};

		string url = _setores[setor];
		string payload = JsonSerializer.Serialize(new { mensagem = mensagem });
		string[] headerArr = { "Content-Type: application/json" };

		http.Request(url, headerArr, HttpClient.Method.Post, payload);
	}
}
