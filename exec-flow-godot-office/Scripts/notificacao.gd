extends CanvasLayer

@onready var painel = $Panel
@onready var texto_label = $Panel/Label
@onready var som = $Som

var posicao_escondida: Vector2
var posicao_visivel: Vector2

func _ready():
	# Calcula as posições baseado no tamanho da tela e do painel
	var largura_tela = get_viewport().get_visible_rect().size.x
	
	# Posição onde ele fica na tela (margem de 20 pixels da direita)
	posicao_visivel = Vector2(largura_tela - painel.size.x - 20, 20)
	
	# Posição escondida (totalmente para fora da tela pela direita)
	posicao_escondida = Vector2(largura_tela + 50, 20)
	
	# Inicia o jogo com o painel escondido
	painel.position = posicao_escondida

func exibir_notificacao(mensagem: String):
	texto_label.text = mensagem
	
	# Toca o arquivo de áudio
	som.play()
	
	# Cria uma animação suave (Tween)
	var tween = create_tween()
	
	# 1. Desliza para dentro da tela (dura 0.5s)
	tween.tween_property(painel, "position", posicao_visivel, 0.5).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	
	# 2. Espera na tela por 4 segundos
	tween.tween_interval(4.0)
	
	# 3. Desliza para fora da tela (dura 0.5s)
	tween.tween_property(painel, "position", posicao_escondida, 0.5).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
