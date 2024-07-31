import Observer


class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self, message: str, error_type: str = "generic"):
        for observer in self._observers:
            observer.update(f"{error_type}: {message}")
