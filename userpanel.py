class UserPanel(object):

    def __init__(self, panel_name: str, panels: dict):
        self.this_panel_name = panel_name
        self.this_panel = panels[self.this_panel_name]
        self.this_panel['panel_obj'] = self
        pass

    def activate(self):
        print('a ' + self.this_panel_name)
        pass

    def deactivate(self):
        print('d ' + self.this_panel_name)
        pass

    def hide(self):
        pass

    def show(self):
        pass