from core.clothing.clothing import ContribClothing


class SpeedGear(ContribClothing):
    def wear(self, wearer, wearstyle, quiet=False):
        if self.db.speed_boost:
            wearer.db.speed_boost = self.db.speed_boost if not wearer.db.speed_boost else wearer.db.speed_boost + self.db.speed_boost
        super().wear(wearer, wearstyle, quiet=False)

    def remove(self, wearer, quiet=False):
        if self.db.speed_boost and wearer.db.speed_boost:
            wearer.db.speed_boost -= self.db.speed_boost
        super().remove(wearer, quiet=False)

