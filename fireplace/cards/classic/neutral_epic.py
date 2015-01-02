from ..utils import *

# Big Game Hunter
class EX1_005:
	action = destroyTarget


# Murloc Warleader
class EX1_507:
	Aura = "EX1_507e"

class EX1_507e:
	Atk = 2
	Health = 1
	def isValidTarget(self, target):
		return target.race == Race.MURLOC and target is not self.source


# Blood Knight
class EX1_590:
	def action(self):
		for target in self.game.board:
			if target.divineShield:
				target.divineShield = False
				self.buff(self, "EX1_590e")

class EX1_590e:
	Atk = 3
	Health = 3


# Molten Giant
class EX1_620:
	@hand
	def UPDATE(self):
		self.cost = self.baseCost - self.controller.hero.damage


# Captain's Parrot
class NEW1_017:
	def action(self):
		pirates = self.controller.deck.filterByRace(Race.PIRATE)
		if pirates:
			self.controller.draw(random.choice(pirates))


# Hungry Crab
class NEW1_017:
	def action(self, target):
		target.destroy()
		self.buff(self, "NEW1_017e")

class NEW1_017e:
	Atk = 2
	Health = 2


# Doomsayer
class NEW1_021:
	def OWN_TURN_BEGIN(self):
		for target in self.controller.getTargets(TARGET_ALL_MINIONS):
			target.destroy()


# Southsea Captain
class NEW1_027:
	Aura = "NEW1_027e"

class NEW1_027e:
	Atk = 1
	Health = 1
	def isValidTarget(self, target):
		return target.race == Race.PIRATE and target is not self.source
