class Data:
    def __init__(self, ui):
        self.ui = ui
        self._coins = 0
        self._health = 5
        self.ui.create_hearts(self._health)

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = value
        self.ui.create_hearts(value)

    @property
    def coins(self):
        return self._coins

    @coins.setter
    def coins(self, value):
        self._coins = value
        if self._coins >= 100:
            self._coins -= 100
            self._health += 1
        self.ui.show_coins(self.coins)

    def reset(self):
        self._coins = 0
        self._health = 5
        self.ui.create_hearts(self._health)
        self.ui.show_coins(self._coins)