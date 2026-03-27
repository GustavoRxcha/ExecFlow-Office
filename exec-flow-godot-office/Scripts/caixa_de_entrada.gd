extends Control

const ARQUIVO_SALVO = "user://caixa_postal.json"
var base_dados = {}
var setor_selecionado = ""

# NOVA VARIÁVEL: Guarda o texto do e-mail que está aberto no momento
var conteudo_atual = ""

@onready var lista_emails = $Panel/MarginContainer/HBoxContainer/AreaConteudo/ListaEmails
@onready var texto_email = $Panel/MarginContainer/HBoxContainer/AreaConteudo/TextoEmail
@onready var btn_copy = $Panel/MarginContainer/HBoxContainer/MenuLateral/BtnCopy
@onready var btn_fechar = $Panel/MarginContainer/HBoxContainer/AreaConteudo/BtnFechar

# Referências dos novos nós
@onready var btn_copiar = $Panel/MarginContainer/HBoxContainer/AreaConteudo/BotoesAcao/BtnCopiar
@onready var btn_baixar = $Panel/MarginContainer/HBoxContainer/AreaConteudo/BotoesAcao/BtnBaixar
@onready var file_dialog = $FileDialog

func _ready():
	self.visible = false
	carregar_dados()
	
	btn_copy.pressed.connect(_on_btn_copy_pressed)
	btn_fechar.pressed.connect(_on_btn_fechar_pressed)
	lista_emails.item_selected.connect(_on_email_selecionado)
	
	# Conecta os novos botões e o FileDialog
	btn_copiar.pressed.connect(_on_btn_copiar_pressed)
	btn_baixar.pressed.connect(_on_btn_baixar_pressed)
	file_dialog.file_selected.connect(_on_file_dialog_file_selected)
	
	# Desativa os botões de ação até que você clique em um e-mail na lista
	btn_copiar.disabled = true
	btn_baixar.disabled = true

func carregar_dados():
	if FileAccess.file_exists(ARQUIVO_SALVO):
		var arquivo = FileAccess.open(ARQUIVO_SALVO, FileAccess.READ)
		var conteudo = arquivo.get_as_text()
		var json = JSON.parse_string(conteudo)
		if json and typeof(json) == TYPE_DICTIONARY:
			base_dados = json

func salvar_dados():
	var arquivo = FileAccess.open(ARQUIVO_SALVO, FileAccess.WRITE)
	arquivo.store_string(JSON.stringify(base_dados, "\t"))

func receber_novo_email(setor: String, titulo: String, conteudo: String):
	if not base_dados.has(setor):
		base_dados[setor] = []

	var data_atual = Time.get_datetime_string_from_system().replace("T", " ")
	base_dados[setor].append({
		"data": data_atual,
		"titulo": titulo,
		"conteudo": conteudo
	})
	salvar_dados()

func _on_btn_copy_pressed():
	abrir_setor("Copy")

func abrir_setor(setor: String):
	setor_selecionado = setor
	lista_emails.clear()
	texto_email.text = "[i]Selecione uma mensagem na lista acima para ler.[/i]"
	
	# Desativa os botões ao mudar de setor
	btn_copiar.disabled = true
	btn_baixar.disabled = true

	if base_dados.has(setor):
		var emails_do_setor = base_dados[setor]
		for i in range(emails_do_setor.size() - 1, -1, -1):
			var email = emails_do_setor[i]
			var titulo_lista = email["data"] + " | " + email["titulo"]
			lista_emails.add_item(titulo_lista)
			lista_emails.set_item_metadata(lista_emails.item_count - 1, i)

func _on_email_selecionado(index: int):
	var index_original = lista_emails.get_item_metadata(index)
	var email = base_dados[setor_selecionado][index_original]
	
	# Atualiza o conteúdo e ativa os botões
	conteudo_atual = email["conteudo"]
	texto_email.text = "[b]" + email["titulo"] + "[/b]\n\n" + conteudo_atual
	
	btn_copiar.disabled = false
	btn_baixar.disabled = false

# --- NOVAS FUNÇÕES DE AÇÃO ---

func _on_btn_copiar_pressed():
	# Copia para a área de transferência do seu computador
	DisplayServer.clipboard_set(conteudo_atual)
	
	# Feedback visual rápido
	btn_copiar.text = "Copiado!"
	await get_tree().create_timer(1.5).timeout
	btn_copiar.text = "Copiar Texto"

func _on_btn_baixar_pressed():
	# Abre a janela do Windows/Mac para você escolher onde salvar (tamanho padrão 600x400)
	file_dialog.popup_centered(Vector2(600, 400))

func _on_file_dialog_file_selected(path: String):
	# Cria e escreve o arquivo .txt no caminho que você escolheu
	var file = FileAccess.open(path, FileAccess.WRITE)
	if file:
		file.store_string(conteudo_atual)
		file.close()
		
		# Feedback visual rápido
		btn_baixar.text = "Salvo!"
		await get_tree().create_timer(1.5).timeout
		btn_baixar.text = "Baixar .txt"

func _on_btn_fechar_pressed():
	self.visible = false
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
