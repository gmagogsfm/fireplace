from fireplace.enums import Zone
from ..card import *


# Cabal Shadow Priest
class EX1_091(Card):
	def action(self, target):
		self.controller.takeControl(target)


# Lightspawn
class EX1_335(Card):
	def UPDATE(self):
		if self.zone == Zone.PLAY and self.atk != self.health:
			# self.atk = self.health
			# Haha! You thought this would be that easy, huh? THINK AGAIN!
			# Attack is the sum of the ATK of the entity and all its slots.
			# This matters because auras are applied to lightspawn, and lightspawn
			# doesn't actually respect those auras.
			# Now, we can either hack around this with internal buffs, tags etc... or we
			# can set the attack to *less* than the health, taking buffs into account.
			# Incidentally, this means that Lightspawn's GameTag.ATK can go negative.
			# Tell me, Blizzard, is it really such a coincidence its base attack is 0?
			self.atk = self.health - self.extraAtk


# Temple Enforcer
class EX1_623(Card):
	action = buffTarget("EX1_623e")

class EX1_623e(Card):
	Health = 3
