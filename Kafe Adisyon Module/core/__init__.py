# core/__init__.py
class AppState:
    def __init__(self):
        self.current_user = None
        self.active_order = None

app_state = AppState()