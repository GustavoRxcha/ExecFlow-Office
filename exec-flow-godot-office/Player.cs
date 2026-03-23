using Godot;
using System;

public partial class Player : CharacterBody3D
{
	public const float Speed = 5.0f;
	public const float JumpVelocity = 4.5f;
	public float gravity = ProjectSettings.GetSetting("physics/3d/default_gravity").AsSingle();

	private Camera3D _camera;
	private float _mouseSensitivity = 0.003f;
	
	// NOVA VARIÁVEL: Referência para o nosso laser
	private RayCast3D _interactRay; 

	public override void _Ready()
	{
		_camera = GetNode<Camera3D>("Camera3D"); 
		
		// NOVA LINHA: Pega o RayCast que colocamos dentro da Câmera
		_interactRay = GetNode<RayCast3D>("Camera3D/RayCast3D"); 
		
		Input.MouseMode = Input.MouseModeEnum.Captured; 
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		if (@event is InputEventMouseMotion mouseMotion)
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

		// NOVA LÓGICA DE INTERAÇÃO
		if (Input.IsActionJustPressed("interagir"))
		{
			if (_interactRay.IsColliding()) // Se o laser bateu em algo
			{
				// Pega o objeto que o laser bateu
				Node3D target = (Node3D)_interactRay.GetCollider(); 
				
				// Verifica se o objeto tem a etiqueta "Interativo"
				if (target.IsInGroup("Interativo"))
				{
					GD.Print("Chefe, você interagiu com: " + target.Name);
					// Aqui no futuro nós vamos abrir a tela de chat do agente!
				}
			}
		}
	}

	public override void _PhysicsProcess(double delta)
	{
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
