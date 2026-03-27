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
	
	private Control _chatGestor;

	public override void _Ready()
	{
		_camera = GetNode<Camera3D>("Camera3D"); 
		_interactRay = GetNode<RayCast3D>("Camera3D/RayCast3D"); 
		
		_chatGestor = GetNode<Control>("ChatGestor");
		Input.MouseMode = Input.MouseModeEnum.Captured; 
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		// 1. Controle de Câmera
		if (@event is InputEventMouseMotion mouseMotion && Input.MouseMode == Input.MouseModeEnum.Captured)
		{
			RotateY(-mouseMotion.Relative.X * _mouseSensitivity);
			_camera.RotateX(-mouseMotion.Relative.Y * _mouseSensitivity);
			
			Vector3 cameraRot = _camera.Rotation;
			cameraRot.X = Mathf.Clamp(cameraRot.X, -Mathf.Pi/2, Mathf.Pi/2);
			_camera.Rotation = cameraRot;
		}

		// 2. Liberar o mouse (tecla Esc / Cancel)
		if (Input.IsActionJustPressed("ui_cancel"))
		{
			Input.MouseMode = Input.MouseModeEnum.Visible;
		}

		// 3. NOVO: Abrir/Fechar a Caixa de Entrada (tecla TAB)
		// Usamos IsActionJustPressed para evitar que a tela fique piscando se segurar a tecla
		if (Input.IsKeyPressed(Key.Tab))
		{
			// Pega a referência da tela de e-mail que está no Autoload
			Node caixaEntrada = GetNode("/root/CaixaDeEntrada");
			
			// Descobre se ela está aberta ou fechada no momento
			bool estaVisivel = (bool)caixaEntrada.Get("visible");
			
			// Inverte o estado (se está aberta, fecha; se está fechada, abre)
			caixaEntrada.Set("visible", !estaVisivel);
			
			if (!estaVisivel) // Se acabou de abrir a tela
			{
				Input.MouseMode = Input.MouseModeEnum.Visible;
				// Já aciona a aba do Copy automaticamente para carregar a lista
				caixaEntrada.Call("abrir_setor", "Copy"); 
			}
			else // Se acabou de fechar a tela
			{
				Input.MouseMode = Input.MouseModeEnum.Captured;
			}
		}

		// 4. Interagir com NPCs e abrir o Tablet de Chat
		if (Input.IsActionJustPressed("interagir"))
		{
			if (_interactRay.IsColliding()) 
			{
				Node3D target = (Node3D)_interactRay.GetCollider(); 
				
				if (target.IsInGroup("Interativo"))
				{
					// Passamos o próprio objeto 'target' e não só o nome
					_chatGestor.Call("configurar_chat", target);
					
					Input.MouseMode = Input.MouseModeEnum.Visible;
					_chatGestor.Visible = true;
				}
			}
		}
	}

	public override void _PhysicsProcess(double delta)
	{
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
