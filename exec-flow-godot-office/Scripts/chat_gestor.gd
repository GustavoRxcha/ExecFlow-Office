extends Control

var setor_id: String = "" 
var npc_atual: Node3D = null # Guarda o NPC com quem estamos a falar

@onready var historico = $Panel/RichTextLabel
@onready var caixa_texto = $Panel/LineEdit

func _ready():
	self.visible = false

# Recebe o objeto do NPC inteiro enviado pelo Player.cs
func configurar_chat(npc_alvo: Node3D):
	npc_atual = npc_alvo
	setor_id = npc_alvo.name
	
	# Verifica se o NPC já tem um histórico guardado
	if npc_alvo.has_method("get_historico"):
		var historico_salvo = npc_alvo.get_historico()
		if historico_salvo != "":
			historico.text = historico_salvo
		else:
			historico.text = "--- Conectado ao Setor: " + setor_id + " ---"
	else:
		historico.text = "--- Conectado ao Setor: " + setor_id + " ---"
		
	caixa_texto.grab_focus()
	_rolar_para_baixo()

func _on_button_pressed():
	enviar_mensagem(caixa_texto.text)

func _on_line_edit_text_submitted(new_text):
	enviar_mensagem(new_text)

func enviar_mensagem(texto: String):
	if texto.strip_edges() == "" or setor_id == "":
		return
		
	historico.text += "\nChefe: " + texto
	historico.text += "\n[SISTEMA]: A aguardar resposta de " + setor_id + "..."
	caixa_texto.text = ""
	
	_atualizar_historico_npc()
	_rolar_para_baixo()
	
	# --- NOVO: DISPARA A ANIMAÇÃO DO NPC ---
	# Se o npc alvo existir e tiver a função de trabalhar, ele ativa a animação no C#
	if npc_atual and npc_atual.has_method("IniciarTrabalho"):
		npc_atual.call("IniciarTrabalho")
	# ----------------------------------------
	
	var cerebro = get_node("/root/CerebroMestre")
	cerebro.call("EnviarOrdem", setor_id, texto, Callable(self, "_receber_resposta_ia"))

func _receber_resposta_ia(resposta: String):
	# Remove a linha de "aguardar resposta" (opcional, mas fica mais limpo)
	historico.text = historico.text.replace("\n[SISTEMA]: A aguardar resposta de " + setor_id + "...", "")
	
	historico.text += "\nGestor: " + resposta
	_atualizar_historico_npc()
	_rolar_para_baixo()

# Guarda o texto atual na memória do NPC
func _atualizar_historico_npc():
	if npc_atual and npc_atual.has_method("salvar_historico"):
		npc_atual.salvar_historico(historico.text)

# Faz o scroll automático para a última mensagem
func _rolar_para_baixo():
	await get_tree().process_frame # Espera um frame para garantir que a UI atualizou
	var scrollbar = historico.get_v_scroll_bar()
	scrollbar.value = scrollbar.max_value

func _on_button_2_pressed() -> void:
	self.visible = false 
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
