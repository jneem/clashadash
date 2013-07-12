class AttackSummary(object):
    class Attack:
        def __init__(self, defender, damageDealt, defenderDead):
            self.defender = defender
            self.damageDealt = damageDealt
            self.defenderDead = defenderDead

    def __init__(self, attacker):
        self.attacker = attacker
        self.attacks = []

    def add(self, defender, damageDealt, defenderDead):
        self.attacks.append(self.Attack(defender, damageDealt, defenderDead))

