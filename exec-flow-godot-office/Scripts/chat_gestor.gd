extends Control

# Agora esta variável começará vazia e será preenchida pelo Player no momento do clique
var setor_id: String = "" 

@onready var historico = $Panel/RichTextLabel
@onready var caixa_texto = $Panel/LineEdit

func _ready():
	# Começa escondido para não atrapalhar a visão inicial
	self.visible = false

# Esta função é a chave! O Player.cs chamará ela ao apertar "E"
func configurar_chat(nome_do_setor: String):
	setor_id = nome_do_setor
	historico.text = "--- Conectado ao Setor: " + setor_id + " ---"
	caixa_texto.grab_focus()

func _on_button_pressed():
	enviar_mensagem(caixa_texto.text)

func _on_line_edit_text_submitted(new_text):
	enviar_mensagem(new_text)

func enviar_mensagem(texto: String):
	if texto.strip_edges() == "" or setor_id == "":
		return
		
	historico.text += "\nChefe: " + texto
	historico.text += "\n[SISTEMA]: Solicitando retorno de " + setor_id + "..."
	caixa_texto.text = ""
	
	# Chama o CérebroMestre (Singleton C#) passando o setor dinâmico
	get_node("/root/CerebroMestre").EnviarOrdem(setor_id, texto, _exibir_resposta)

func _exibir_resposta(resposta: String):
	historico.text += "\nGestor: " + resposta

func _on_button_2_pressed() -> void:
	self.visible = false 
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
