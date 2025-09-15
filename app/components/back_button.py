from kivy.uix.button import Button
# Import des boutons KivyMD

class BackButton(Button):
    def __init__(self, target_screen=None, **kwargs):
        super().__init__(**kwargs)
        self.icon = "arrow-left"  # icône flèche gauche classique
        self.user_font_size = "24sp"
        self.md_bg_color = (0, 0, 0, 0)  # transparent (pas de fond)
        self.size_hint = (None, None)
        self.size = ("48dp", "48dp")
        self.target_screen = target_screen
        self.on_release = self.go_back

    def go_back(self, *args):
        if self.target_screen and self.parent:
            # Remonte la hiérarchie jusqu'au ScreenManager
            screen_manager = self.parent
            while screen_manager and not hasattr(screen_manager, 'current'):
                screen_manager = screen_manager.parent
            if screen_manager and hasattr(screen_manager, 'current'):
                screen_manager.current = self.target_screen
