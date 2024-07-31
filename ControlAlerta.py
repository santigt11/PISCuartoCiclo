from Observer import Observer


class ErrorLogger(Observer):
    def update(self, message: str):
        print(f"Error logged: {message}")

class ErrorNotifier(Observer):
    def update(self, message: str):
        # Aquí puedes implementar la lógica para enviar una notificación, por ejemplo, por correo electrónico.
        print(f"Notification sent: {message}")