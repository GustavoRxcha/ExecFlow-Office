using Godot;
using System;

public partial class GestorCopy : CharacterBody3D
{
	// Onde vamos encaixar o carrinho invisível (o Carrinho/PathFollow3D)
	[Export] public PathFollow3D CarrinhoTrilho; 
	
	private AnimationPlayer _animPlayer;
	private bool _estaCaminhando = false;

	public override void _Ready()
	{
		// Acha o AnimationPlayer dentro do Gestor
		_animPlayer = GetNodeOrNull<AnimationPlayer>("AnimationPlayer");
		
		// NOVA LINHA: Força o personagem a começar o jogo na animação de ficar parado!
		if (_animPlayer != null) _animPlayer.Play("Idle");
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		// Ao apertar T, ele começa a andar, se houver um trilho
		if (Input.IsKeyPressed(Key.T) && CarrinhoTrilho != null && !_estaCaminhando)
		{
			IniciarCaminhada();
		}
	}

	private void IniciarCaminhada()
	{
		_estaCaminhando = true;
		
		// Força o carrinho a zerar e voltar para o ponto de início (0.0)
		CarrinhoTrilho.ProgressRatio = 0.0f; 
		
		// Toca a animação de andar. 
		// ATENÇÃO: Verifique se o nome é "Walk" mesmo no seu projeto!
		if (_animPlayer != null) _animPlayer.Play("Walk");

		// Cria o motor de deslizar
		Tween tween = CreateTween();
		
		// Tempo da caminhada em segundos (você pode aumentar ou diminuir depois)
		float tempoDeViagem = 4.0f; 
		
		// Manda o "progresso" do carrinho ir de 0 (começo) a 1 (fim) da linha
		tween.TweenProperty(CarrinhoTrilho, "progress_ratio", 1.0f, tempoDeViagem);
		
		// Avisa o que fazer quando a viagem terminar
		tween.Finished += AoChegar;
	}

	public override void _PhysicsProcess(double delta)
	{
		if (_estaCaminhando && CarrinhoTrilho != null)
		{
			// TRUQUE 1: Copia o X e o Z do carrinho, mas TRAVA o Y (altura) 
			// na altura atual do próprio Gestor. Adeus fantasma voador!
			GlobalPosition = new Vector3(
				CarrinhoTrilho.GlobalPosition.X, 
				GlobalPosition.Y, 
				CarrinhoTrilho.GlobalPosition.Z
			);
			
			// TRUQUE 2: Pega a rotação do carrinho
			Vector3 rotacaoCarrinho = CarrinhoTrilho.GlobalRotation;
			
			// Mathf.Pi equivale a 180 graus. Isso vira o boneco para ele andar de frente!
			GlobalRotation = new Vector3(0, rotacaoCarrinho.Y + Mathf.Pi, 0);
		}
	}

	private void AoChegar()
	{
		_estaCaminhando = false;
		
		// Toca a animação de ficar parado (Lembre de checar o nome exato, ex: "Idle")
		if (_animPlayer != null) _animPlayer.Play("Idle");
		
		GD.Print("Chegou perfeitamente pelo trilho!");
	}
}
