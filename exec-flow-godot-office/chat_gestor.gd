extends Control

# Criamos referências diretas aos elementos do ecrã
@onready var historico = $Panel/RichTextLabel
@onready var caixa_texto = $Panel/LineEdit

func _ready():
	# Assim que a janela abre, o cursor já vai direto para a caixa de texto
	caixa_texto.grab_focus()

# Esta função roda quando clica no botão "Enviar"
func _on_button_pressed():
	enviar_mensagem(caixa_texto.text)

# Esta função roda quando aperta a tecla "Enter"
func _on_line_edit_text_submitted(new_text):
	enviar_mensagem(new_text)

# O motor principal do nosso chat
func enviar_mensagem(texto: String):
	# Se a mensagem estiver vazia, não faz nada
	if texto.strip_edges() == "":
		return
		
	# Adiciona a mensagem do Chefe no histórico
	historico.text += "\nChefe: " + texto
	
	# Limpa a caixa de texto para a próxima ordem
	caixa_texto.text = ""
	
	# Aqui no futuro chamaremos o Python (IA) para gerar a resposta!


func _on_button_2_pressed() -> void:
	self.visible = false # Esconde o chat
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED # Trava o mouse de volta no jogo
