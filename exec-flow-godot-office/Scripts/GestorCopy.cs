using Godot;
using System;

public partial class GestorCopy : CharacterBody3D
{
	[Export] public PathFollow3D CarrinhoTrilho; 
	
	private AnimationPlayer _animPlayer;
	
	// Controles de Estado
	private bool _ocupado = false; 
	private bool _estaCaminhando = false; 
	private bool _indoParaDestino = true; 

	private string _historicoConversa = "";

	public override void _Ready()
	{
		_animPlayer = GetNodeOrNull<AnimationPlayer>("AnimationPlayer");
		// Ao iniciar, força a rotação padrão de olhar para frente
		RotationDegrees = new Vector3(0, -90f, 0);
		if (_animPlayer != null) _animPlayer.Play("Idle");
	}

	// --- MÉTODO CHAMADO PELO CHAT QUANDO A MENSAGEM É ENVIADA ---
	public void IniciarTrabalho()
	{
		if (_ocupado) return; 
		
		_ocupado = true;
		IrParaMesaCopy();
	}

	private void IrParaMesaCopy()
	{
		_estaCaminhando = true;
		_indoParaDestino = true;
		if (_animPlayer != null) _animPlayer.Play("Walk");

		Tween tween = CreateTween();
		float tempoDeViagem = 4.0f; 
		tween.TweenProperty(CarrinhoTrilho, "progress_ratio", 1.0f, tempoDeViagem);
		tween.Finished += AoChegarNaMesa;
	}

	private async void AoChegarNaMesa()
	{
		_estaCaminhando = false;
		
		// Opcional: Se ele ficar torto na mesa do copywriter, 
		// você pode forçar uma rotação específica aqui também, ex:
		// RotationDegrees = new Vector3(0, 90f, 0); 
		
		if (_animPlayer != null) _animPlayer.Play("Idle"); 

		await ToSignal(GetTree().CreateTimer(15.0f), SceneTreeTimer.SignalName.Timeout);

		RetornarParaMesaGestor();
	}

	private void RetornarParaMesaGestor()
	{
		_estaCaminhando = true;
		_indoParaDestino = false;
		if (_animPlayer != null) _animPlayer.Play("Walk");

		Tween tween = CreateTween();
		float tempoDeViagem = 4.0f; 
		tween.TweenProperty(CarrinhoTrilho, "progress_ratio", 0.0f, tempoDeViagem);
		tween.Finished += AoChegarDeVolta;
	}

	private void AoChegarDeVolta()
	{
		_estaCaminhando = false;
		_ocupado = false; 
		
		// --- CORREÇÃO AQUI ---
		// Força a rotação exata desejada (-90 graus no eixo Y) para olhar para frente,
		// ignorando qualquer rotação residual do trilho.
		RotationDegrees = new Vector3(0, -90f, 0);
		// ---------------------

		if (_animPlayer != null) _animPlayer.Play("Idle");
	}

	public override void _PhysicsProcess(double delta)
	{
		// A lógica de rotação dinâmica só roda enquanto ele está caminhando
		if (_estaCaminhando && CarrinhoTrilho != null)
		{
			GlobalPosition = new Vector3(
				CarrinhoTrilho.GlobalPosition.X, 
				GlobalPosition.Y, 
				CarrinhoTrilho.GlobalPosition.Z
			);
			
			Vector3 rotacaoCarrinho = CarrinhoTrilho.GlobalRotation;
			
			float ajusteRotacao = _indoParaDestino ? Mathf.Pi : 0;
			GlobalRotation = new Vector3(0, rotacaoCarrinho.Y + ajusteRotacao, 0);
		}
	}

	// Funções de Persistência do Histórico
	public void salvar_historico(string texto) 
	{
		_historicoConversa = texto;
	}

	public string get_historico() 
	{
		return _historicoConversa;
	}
}
