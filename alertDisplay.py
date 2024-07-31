from Observer import Observer


class AlertDisplay(Observer):
    def update(self, message: str):
        # Aquí podrías implementar la lógica para mostrar una alerta en la interfaz de usuario
        print(f"Alert: {message}")
