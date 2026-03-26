using Godot;
using System;

public partial class Player : CharacterBody3D
{
	public const float Speed = 5.0f;
	public const float JumpVelocity = 4.5f;
	public float gravity = ProjectSettings.GetSetting("physics/3d/default_gravity").AsSingle();

	private Camera3D _camera;
	private float _mouseSensitivity = 0.003f;
	private RayCast3D _interactRay; 
	
	// Referência para a nossa tela de Chat (Tablet)
	private Control _chatGestor;

	public override void _Ready()
	{
		_camera = GetNode<Camera3D>("Camera3D"); 
		_interactRay = GetNode<RayCast3D>("Camera3D/RayCast3D"); 
		
		// Pega o ChatGestor que você arrastou para dentro do Player
		_chatGestor = GetNode<Control>("ChatGestor");
		
		Input.MouseMode = Input.MouseModeEnum.Captured; 
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		// Só permite girar a cabeça se o mouse estiver travado no jogo (Chat fechado)
		if (@event is InputEventMouseMotion mouseMotion && Input.MouseMode == Input.MouseModeEnum.Captured)
		{
			RotateY(-mouseMotion.Relative.X * _mouseSensitivity);
			_camera.RotateX(-mouseMotion.Relative.Y * _mouseSensitivity);
			
			Vector3 cameraRot = _camera.Rotation;
			cameraRot.X = Mathf.Clamp(cameraRot.X, -Mathf.Pi/2, Mathf.Pi/2);
			_camera.Rotation = cameraRot;
		}

		if (Input.IsActionJustPressed("ui_cancel"))
		{
			Input.MouseMode = Input.MouseModeEnum.Visible;
		}

		// LÓGICA DE INTERAÇÃO DINÂMICA COM OS GESTORES
		if (Input.IsActionJustPressed("interagir"))
		{
			if (_interactRay.IsColliding()) 
			{
				Node3D target = (Node3D)_interactRay.GetCollider(); 
				
				if (target.IsInGroup("Interativo"))
				{
					// Pega o nome do nó no Godot (ex: "Copy" ou "TI")
					string nomeSetor = target.Name; 
					
					// Injeta o nome no script GDScript do Chat para torná-lo dinâmico
					_chatGestor.Call("configurar_chat", nomeSetor);
					
					// Destrava o mouse para você poder clicar no tablet
					Input.MouseMode = Input.MouseModeEnum.Visible;
					
					// Abre o Tablet na tela
					_chatGestor.Visible = true;
				}
			}
		}
	}

	public override void _PhysicsProcess(double delta)
	{
		// Se o Chat estiver aberto, o jogador fica parado
		if (_chatGestor.Visible)
		{
			Velocity = Vector3.Zero;
			return;
		}

		Vector3 velocity = Velocity;

		if (!IsOnFloor())
			velocity.Y -= gravity * (float)delta;

		if (Input.IsActionJustPressed("ui_accept") && IsOnFloor())
			velocity.Y = JumpVelocity;

		Vector2 inputDir = Input.GetVector("ui_left", "ui_right", "ui_up", "ui_down");
		Vector3 direction = (Transform.Basis * new Vector3(inputDir.X, 0, inputDir.Y)).Normalized();
		
		if (direction != Vector3.Zero)
		{
			velocity.X = direction.X * Speed;
			velocity.Z = direction.Z * Speed;
		}
		else
		{
			velocity.X = Mathf.MoveToward(Velocity.X, 0, Speed);
			velocity.Z = Mathf.MoveToward(Velocity.Z, 0, Speed);
		}

		Velocity = velocity;
		MoveAndSlide();
	}
}
