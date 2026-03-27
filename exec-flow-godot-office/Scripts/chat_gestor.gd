extends Control

var setor_id: String = "" 
var npc_atual: Node3D = null 
var ultimo_pedido: String = "" # <-- NOVO: Guarda o pedido para usar como título

@onready var historico = $Panel/RichTextLabel
@onready var caixa_texto = $Panel/LineEdit

func _ready():
	self.visible = false

func configurar_chat(npc_alvo: Node3D):
	npc_atual = npc_alvo
	setor_id = npc_alvo.name
	
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
		
	ultimo_pedido = texto # Guarda o que você digitou
		
	historico.text += "\nChefe: " + texto
	historico.text += "\n[SISTEMA]: A aguardar resposta de " + setor_id + "..."
	caixa_texto.text = ""
	
	_atualizar_historico_npc()
	_rolar_para_baixo()
	
	if npc_atual and npc_atual.has_method("IniciarTrabalho"):
		npc_atual.call("IniciarTrabalho")
	
	var cerebro = get_node("/root/CerebroMestre")
	cerebro.call("EnviarOrdem", setor_id, texto, Callable(self, "_receber_resposta_ia"))

# --- A MÁGICA ACONTECE AQUI ---
func _receber_resposta_ia(resposta: String):
	# Limpa a mensagem de "aguardando"
	historico.text = historico.text.replace("\n[SISTEMA]: A aguardar resposta de " + setor_id + "...", "")
	
	# Avisa no tablet que o e-mail chegou
	historico.text += "\n[SISTEMA]: Tarefa concluída! O resultado foi enviado para a sua Caixa de Entrada."
	_atualizar_historico_npc()
	_rolar_para_baixo()
	
	# Cria um título curto (pega as primeiras 35 letras do seu pedido)
	var titulo_email = ultimo_pedido
	if titulo_email.length() > 35:
		titulo_email = titulo_email.substr(0, 35) + "..."
		
	
	# Manda o Título e o Texto da IA para salvar no JSON da Caixa de Entrada
	get_node("/root/CaixaDeEntrada").call("receber_novo_email", setor_id, titulo_email, resposta)
	
	# --- NOVO: DISPARA A NOTIFICAÇÃO VISUAL E SONORA ---
	get_node("/root/Notificacao").call("exibir_notificacao", "Novo arquivo de " + setor_id + " na Caixa de Entrada!")
	
func _atualizar_historico_npc():
	if npc_atual and npc_atual.has_method("salvar_historico"):
		npc_atual.salvar_historico(historico.text)

func _rolar_para_baixo():
	await get_tree().process_frame 
	var scrollbar = historico.get_v_scroll_bar()
	scrollbar.value = scrollbar.max_value

func _on_button_2_pressed() -> void:
	self.visible = false 
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
