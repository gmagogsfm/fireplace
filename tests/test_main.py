#!/usr/bin/env python
import sys; sys.path.append("..")
import fireplace
import logging
import random
from fireplace.heroes import *
from fireplace.enums import *
from fireplace.utils import randomDraft


MOONFIRE = "CS2_008"
WISP = "CS2_231"
CIRCLE_OF_HEALING = "EX1_621"
DREAM = "DREAM_04"
SILENCE = "EX1_332"
SPELLBENDERT = "tt_010a"
THE_COIN = "GAME_005"
RESTORE_1 = "XXX_003"

logging.getLogger().setLevel(logging.DEBUG)


def prepare_game(hero1=MAGE, hero2=WARRIOR):
	print("Initializing a new game")
	deck1 = randomDraft(hero=hero1)
	deck2 = randomDraft(hero=hero2)
	player1 = fireplace.Player(name="Player1", deck=deck1)
	player2 = fireplace.Player(name="Player2", deck=deck2)
	game = fireplace.Game(players=(player1, player2))
	game.start()

	return game


def test_positioning():
	game = prepare_game()
	wisp1 = game.currentPlayer.give(WISP)
	wisp1.play()
	wisp2 = game.currentPlayer.give(WISP)
	wisp2.play()
	wisp3 = game.currentPlayer.give(WISP)
	wisp3.play()

	assert wisp1.adjacentMinions == [wisp2]
	assert wisp2.adjacentMinions == [wisp1, wisp3]
	assert wisp3.adjacentMinions == [wisp2]
	game.endTurn(); game.endTurn()
	flametongue = game.currentPlayer.give("EX1_565")
	flametongue.play()
	wisp4 = game.currentPlayer.give(WISP)
	wisp4.play()
	assert flametongue.aura
	assert wisp3.buffs, wisp3.buffs
	assert wisp3.buffs.contains(flametongue.aura)
	assert wisp1.atk == 1, wisp1.atk
	assert wisp2.atk == 1
	assert wisp3.atk == 3, wisp3.atk
	assert flametongue.atk == 0, flametongue.atk
	assert flametongue.adjacentMinions == [wisp3, wisp4]
	assert wisp4.atk == 3, wisp4.atk


def test_armor():
	game = prepare_game(WARRIOR, WARRIOR)
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	assert game.currentPlayer.hero.armor == 0
	assert not game.currentPlayer.hero.power.exhausted
	assert game.currentPlayer.hero.power.isPlayable()
	game.currentPlayer.hero.power.play()
	assert game.currentPlayer.hero.power.exhausted
	assert not game.currentPlayer.hero.power.isPlayable()
	assert game.currentPlayer.hero.armor == 2
	assert game.currentPlayer.mana == 2
	game.endTurn()
	axe = game.currentPlayer.give("CS2_106")
	axe.play()
	assert axe is game.currentPlayer.hero.weapon
	assert axe in game.currentPlayer.hero.slots
	assert game.currentPlayer.hero.atk == 3
	game.currentPlayer.hero.attack(game.currentPlayer.opponent.hero)
	assert game.currentPlayer.opponent.hero.health == 29
	assert game.currentPlayer.opponent.hero.armor == 0


def test_freeze():
	game = prepare_game()
	flameimp = game.currentPlayer.give("EX1_319")
	flameimp.play()
	game.endTurn()

	frostshock = game.currentPlayer.give("CS2_037")
	frostshock.play(target=flameimp)
	assert flameimp.frozen
	game.endTurn()

	assert flameimp.frozen
	assert not flameimp.canAttack()
	game.endTurn()
	assert not flameimp.frozen
	game.endTurn()

	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	wisp.frozen = True
	assert wisp.frozen
	game.endTurn()
	assert not wisp.frozen


def test_spell_power():
	game = prepare_game(HUNTER, HUNTER)
	game.endTurn(); game.endTurn()

	expectedHealth = 30
	assert game.player2.hero.health == expectedHealth
	game.currentPlayer.give(MOONFIRE).play(target=game.player2.hero); expectedHealth -= 1
	assert game.player2.hero.health == expectedHealth
	# Play a kobold
	game.currentPlayer.give("CS2_142").play()
	game.currentPlayer.give(MOONFIRE).play(target=game.player2.hero); expectedHealth -= 1+1
	assert game.player2.hero.health == expectedHealth
	# Summon Malygos
	malygos = game.currentPlayer.summon("EX1_563")
	game.currentPlayer.give(MOONFIRE).play(target=game.player2.hero); expectedHealth -= 1+1+5
	assert game.player2.hero.health == expectedHealth
	# Test heals are not affected
	game.currentPlayer.give(RESTORE_1).play(target=game.player2.hero); expectedHealth += 1
	assert game.player2.hero.health == expectedHealth
	game.endTurn(); game.endTurn()

	# Check hero power is unaffected
	game.currentPlayer.hero.power.play(); expectedHealth -= 2
	assert game.player2.hero.health == expectedHealth
	# Check battlecries are unaffected
	game.currentPlayer.give("CS2_189").play(target=game.player2.hero); expectedHealth -= 1
	assert game.player2.hero.health == expectedHealth

	game.endTurn(); game.endTurn()
	malygos.destroy()
	# Check arcane missiles doesn't wreck everything
	game.currentPlayer.give("EX1_277").play(); expectedHealth -= 3+1
	assert game.player2.hero.health == expectedHealth


def test_mage():
	game = prepare_game(MAGE, MAGE)
	assert game.currentPlayer.hero.id is MAGE
	game.endTurn(); game.endTurn()

	assert game.currentPlayer.hero.health == 30
	assert game.currentPlayer.opponent.hero.health == 30

	# Fireblast the opponent hero
	game.currentPlayer.hero.power.play(target=game.currentPlayer.opponent.hero)
	assert game.currentPlayer.hero.health == 30
	assert game.currentPlayer.opponent.hero.health == 29
	assert not game.currentPlayer.hero.power.isPlayable()


def test_priest():
	game = prepare_game(PRIEST, PRIEST)
	assert game.currentPlayer.hero.id is PRIEST
	game.endTurn(); game.endTurn()
	# Heal self
	assert game.currentPlayer.hero.health == 30
	game.currentPlayer.hero.power.play(target=game.currentPlayer.hero)
	assert game.currentPlayer.hero.health == 30

	game.endTurn(); game.endTurn()
	# moonfire self
	moonfire = game.currentPlayer.give(MOONFIRE).play(target=game.currentPlayer.hero)
	assert game.currentPlayer.hero.health == 29
	game.currentPlayer.hero.power.play(target=game.currentPlayer.hero)
	assert game.currentPlayer.hero.health == 30
	assert not game.currentPlayer.hero.power.isPlayable()


def test_shaman():
	game = prepare_game(SHAMAN, SHAMAN)
	assert game.currentPlayer.hero.id is SHAMAN
	game.endTurn(); game.endTurn()
	assert len(game.currentPlayer.hero.power.data.entourage) == 4
	game.currentPlayer.hero.power.play()
	assert game.currentPlayer.field[0].id in ("CS2_050", "CS2_051", "CS2_052", "NEW1_009")


def test_paladin():
	game = prepare_game(PALADIN, PALADIN)
	assert game.currentPlayer.hero.id is PALADIN
	game.endTurn(); game.endTurn()
	game.currentPlayer.hero.power.play()
	assert len(game.board) == 1
	assert len(game.currentPlayer.field) == 1
	assert game.currentPlayer.field[0].id == "CS2_101t"


def test_deathrattle():
	game = prepare_game()
	game.endTurn(); game.endTurn()

	loothoarder = game.currentPlayer.give("EX1_096")
	loothoarder.play()
	cardcount = len(game.currentPlayer.hand)
	game.endTurn()

	archer = game.currentPlayer.give("CS2_189")
	archer.play(target=loothoarder)
	assert loothoarder.zone == Zone.GRAVEYARD
	assert loothoarder.damage == 0
	assert len(game.currentPlayer.opponent.hand) == cardcount + 1
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	# test soul of the forest: deathrattle in slots
	assert not archer.hasDeathrattle
	sotf = game.currentPlayer.give("EX1_158")
	sotf.play()
	assert len(archer.slots) == 1
	assert len(game.currentPlayer.field) == 1
	game.currentPlayer.give(MOONFIRE).play(target=archer)
	assert archer.zone == Zone.GRAVEYARD
	assert len(game.currentPlayer.field) == 1


def test_cult_master():
	game = prepare_game()
	cultmaster = game.currentPlayer.give("EX1_595")

	wisp1 = game.currentPlayer.give(WISP)
	wisp1.play()
	wisp2 = game.currentPlayer.give(WISP)
	wisp2.play()

	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	cultmaster.play()
	assert len(game.currentPlayer.hand) == 7
	game.currentPlayer.give(MOONFIRE).play(target=wisp1)
	assert len(game.currentPlayer.hand) == 8

	# Make sure cult master doesn't draw off itself
	game.currentPlayer.give(MOONFIRE).play(target=cultmaster)
	game.currentPlayer.give(MOONFIRE).play(target=cultmaster)
	assert len(game.currentPlayer.hand) == 8

	game.currentPlayer.give(MOONFIRE).play(target=wisp2)
	assert len(game.currentPlayer.hand) == 8


def test_mana():
	game = prepare_game()
	footman = game.currentPlayer.give("CS1_042")
	assert footman.cost == 1
	footman.play()
	assert footman.atk == 1
	assert footman.health == 2
	game.endTurn()

	# Play the coin
	coin = game.currentPlayer.getById(THE_COIN)
	coin.play()
	assert game.currentPlayer.mana == 2
	assert game.currentPlayer.tempMana == 1
	game.endTurn()
	assert game.currentPlayer.opponent.tempMana == 0
	assert game.currentPlayer.opponent.mana == 1, game.currentPlayer.opponent.mana

	game.endTurn(); game.endTurn()

	assert game.currentPlayer.mana == 3
	assert game.currentPlayer.maxMana == 3
	felguard = game.currentPlayer.give("EX1_301")
	felguard.play()
	assert game.currentPlayer.mana == 0, game.currentPlayer.mana
	assert game.currentPlayer.maxMana == 2, game.currentPlayer.maxMana


def test_overload():
	game = prepare_game()
	dustdevil = game.currentPlayer.give("EX1_243")
	dustdevil.play()
	assert game.currentPlayer.overloaded == 2
	game.endTurn(); game.endTurn()
	assert game.currentPlayer.mana == 0


def test_charge():
	game = prepare_game()
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	assert not wisp.charge
	assert not wisp.canAttack()
	# play Charge on wisp
	game.currentPlayer.give("CS2_103").play(target=wisp)
	assert wisp.buffs[0].tags[GameTag.CHARGE]
	assert wisp.charge
	assert wisp.canAttack()
	wisp.attack(game.currentPlayer.opponent.hero)
	assert not wisp.canAttack()
	game.endTurn()
	game.currentPlayer.getById(THE_COIN).play()
	wolfrider = game.currentPlayer.give("CS2_124")
	wolfrider.play()
	assert wolfrider.charge
	assert wolfrider.canAttack()
	game.endTurn()
	assert wisp.canAttack()
	wisp.attack(game.currentPlayer.opponent.hero)
	assert not wisp.canAttack()
	game.endTurn()
	watcher = game.currentPlayer.give("EX1_045")
	watcher.play()
	assert not watcher.canAttack()
	game.currentPlayer.give("CS2_103").play(target=watcher)
	assert not watcher.canAttack()
	game.endTurn(); game.endTurn()
	assert not watcher.canAttack()
	watcher.silence()
	assert watcher.canAttack()


def test_divine_shield():
	game = prepare_game()
	squire = game.currentPlayer.give("EX1_008")
	squire.play()
	assert squire.divineShield
	game.endTurn()

	archer = game.currentPlayer.give("CS2_189")
	archer.play(target=squire)
	assert len(game.currentPlayer.field) == 1
	assert not squire.divineShield
	game.currentPlayer.getById(THE_COIN).play()
	archer2 = game.currentPlayer.give("CS2_189")
	archer2.play(target=squire)
	assert len(game.currentPlayer.opponent.field) == 0
	assert not squire.divineShield


def test_silence():
	game = prepare_game()
	silence = game.currentPlayer.give(SILENCE)
	thrallmar = game.currentPlayer.give("EX1_021")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	thrallmar.play()
	assert thrallmar.windfury
	silence.play(target=thrallmar)
	assert not thrallmar.windfury


def test_earth_shock():
	game = prepare_game()
	crusader = game.currentPlayer.give("EX1_020")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	crusader.play()
	assert crusader.divineShield
	game.endTurn()
	earthshock = game.currentPlayer.give("EX1_245")
	earthshock.play(target=crusader)
	assert crusader.zone == Zone.GRAVEYARD


def test_equality():
	game = prepare_game()
	equality = game.currentPlayer.give("EX1_619")
	# summon a bunch of big dudes
	game.currentPlayer.summon("CS2_186")
	game.currentPlayer.summon("CS2_186")
	game.currentPlayer.opponent.summon("CS2_186")
	game.currentPlayer.opponent.summon("CS2_186")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	# And a violet teacher too, why not
	game.currentPlayer.summon("NEW1_026")

	pyro = game.currentPlayer.give("NEW1_020")
	pyro.play()
	assert len(game.board) == 6
	equality.play()
	assert not game.board


def test_stealth_windfury():
	game = prepare_game(MAGE, MAGE)
	worgen = game.currentPlayer.give("EX1_010")
	worgen.play()
	assert worgen.stealthed
	assert not worgen.canAttack()
	game.endTurn()

	archer = game.currentPlayer.give("CS2_189")
	assert len(archer.targets) == 2  # Only the heroes
	game.currentPlayer.getById(THE_COIN).play()
	assert len(game.currentPlayer.hero.power.targets) == 2
	game.endTurn()

	worgen.attack(game.currentPlayer.opponent.hero)
	assert not worgen.stealthed
	assert not worgen.canAttack()
	windfury = game.currentPlayer.give("CS2_039")
	windfury.play(target=worgen)
	assert worgen.canAttack()
	worgen.attack(game.currentPlayer.opponent.hero)
	assert not worgen.canAttack()
	game.endTurn()

	assert len(archer.targets) == 3


def test_tags():
	game = prepare_game()

	alakir = game.currentPlayer.give("NEW1_010")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	alakir.play()
	assert alakir.tags[GameTag.CHARGE]
	assert alakir.charge
	assert alakir.tags[GameTag.DIVINE_SHIELD]
	assert alakir.divineShield
	assert alakir.tags[GameTag.TAUNT]
	assert alakir.taunt
	assert alakir.tags[GameTag.WINDFURY]
	assert alakir.windfury


def test_card_draw():
	game = prepare_game()
	# pass turn 1
	game.endTurn()
	game.endTurn()

	# novice should draw 1 card
	card = game.currentPlayer.give("EX1_015")
	handlength = len(game.currentPlayer.hand)
	card.play()
	# hand should be 1 card played, 1 card drawn; same length
	assert len(game.currentPlayer.hand) == handlength
	game.endTurn()

	# succubus should discard 1 card
	card = game.currentPlayer.give("EX1_306")
	handlength = len(game.currentPlayer.hand)
	card.play()
	assert len(game.currentPlayer.hand) == handlength - 2


def test_deathwing():
	game = prepare_game()
	deathwing = game.currentPlayer.give("NEW1_030")
	# play some wisps
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()

	# fast-forward to turn 10
	for i in range(9 * 2):
		game.endTurn()

	deathwing.play()
	assert not game.currentPlayer.hand
	assert len(game.board) == 1


def test_combo():
	game = prepare_game()
	game.endTurn(); game.endTurn()
	game.endTurn()
	game.currentPlayer.getById(THE_COIN).play()
	# SI:7 with combo
	assert game.currentPlayer.tags[GameTag.COMBO_ACTIVE]
	game.currentPlayer.give("EX1_134").play(target=game.currentPlayer.hero)
	assert game.currentPlayer.hero.health == 28
	game.endTurn()

	# Without combo should not have a target
	assert not game.currentPlayer.tags[GameTag.COMBO_ACTIVE]
	game.currentPlayer.give("EX1_134").play()


def test_power_word_shield():
	game = prepare_game()
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	assert wisp.health == 1
	assert len(game.currentPlayer.hand) == 4

	pwshield = game.currentPlayer.give("CS2_004")
	pwshield.play(target=wisp)
	assert wisp.health == 3
	assert len(game.currentPlayer.hand) == 5

	wisp.silence()
	assert wisp.health == 1


def test_kill_command():
	game = prepare_game(HUNTER, HUNTER)
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	kc = game.currentPlayer.give("EX1_539")
	kc.play(target=game.currentPlayer.opponent.hero)
	assert game.currentPlayer.opponent.hero.health == 27
	game.endTurn(); game.endTurn()

	# play a timber wolf before this time
	game.currentPlayer.give("DS1_175").play()
	kc = game.currentPlayer.give("EX1_539")
	kc.play(target=game.currentPlayer.opponent.hero)
	assert game.currentPlayer.opponent.hero.health == 22


def test_ancestral_healing():
	game = prepare_game()
	ancestral = game.currentPlayer.give("CS2_041")
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	assert not wisp.taunt
	ancestral.play(wisp)
	assert wisp.health == 1
	assert wisp.taunt


def test_alarmobot():
	game = prepare_game()
	bot = game.currentPlayer.give("EX1_006")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	bot.play()
	game.currentPlayer.discardHand()
	wisp = game.currentPlayer.give(WISP)
	assert bot.zone == Zone.PLAY
	assert wisp.zone == Zone.HAND
	game.endTurn(); game.endTurn()
	assert bot.zone == Zone.HAND
	assert wisp.zone == Zone.PLAY
	assert len(game.currentPlayer.field) == 1

	# bot should not trigger if hand has no minions
	bot.play()
	game.currentPlayer.discardHand()
	game.endTurn(); game.endTurn()
	assert bot.zone == Zone.PLAY
	assert len(game.currentPlayer.field) == 2


def test_doomhammer():
	game = prepare_game()
	doomhammer = game.currentPlayer.give("EX1_567")

	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	assert not game.currentPlayer.hero.atk
	assert not game.currentPlayer.hero.windfury
	doomhammer.play()
	assert game.currentPlayer.hero.atk == 2
	assert game.currentPlayer.hero.windfury
	assert game.currentPlayer.hero.weapon.durability == 8
	game.currentPlayer.hero.attack(target=game.currentPlayer.opponent.hero)
	assert game.currentPlayer.hero.canAttack()
	game.currentPlayer.hero.attack(target=game.currentPlayer.opponent.hero)
	assert not game.currentPlayer.hero.canAttack()
	assert game.currentPlayer.hero.weapon.durability == 6


def test_raging_worgen():
	game = prepare_game()
	worgen = game.currentPlayer.summon("EX1_412")
	assert worgen.health == 3
	game.currentPlayer.give(MOONFIRE).play(target=worgen)
	assert worgen.health == 2
	assert worgen.atk == 4
	assert worgen.windfury
	game.currentPlayer.give(CIRCLE_OF_HEALING).play()
	assert worgen.atk == 3
	assert not worgen.windfury


def test_spiteful_smith():
	game = prepare_game()
	assert not game.currentPlayer.hero.atk
	smith = game.currentPlayer.summon("CS2_221")
	assert smith.health == 6
	assert not game.currentPlayer.hero.atk
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	axe = game.currentPlayer.give("CS2_106")
	axe.play()
	assert axe.atk == 3
	assert game.currentPlayer.hero.atk == 3
	assert not game.currentPlayer.opponent.hero.atk
	game.currentPlayer.give(MOONFIRE).play(target=smith)
	assert smith.health == 5
	assert axe.atk == 5
	assert axe.buffs
	assert game.currentPlayer.hero.atk == 5
	assert not game.currentPlayer.opponent.hero.atk
	game.currentPlayer.give(CIRCLE_OF_HEALING).play()
	assert axe.atk == 3
	assert game.currentPlayer.hero.atk == 3
	game.currentPlayer.give(MOONFIRE).play(target=smith)
	assert smith.health == 5
	assert axe.atk == 5
	assert game.currentPlayer.hero.atk == 5


def test_sword_of_justice():
	game = prepare_game(PALADIN, PALADIN)
	sword = game.currentPlayer.give("EX1_366")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	sword.play()
	assert sword.durability == 5
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	assert wisp.atk == 2
	assert wisp.health == 2
	assert wisp.buffs
	assert sword.durability == 4
	game.endTurn()

	game.currentPlayer.give(WISP).play()
	assert sword.durability == 4
	game.endTurn()

	game.currentPlayer.hero.power.play()
	assert sword.durability == 3

	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	assert not game.currentPlayer.hero.weapon
	wisp2 = game.currentPlayer.give(WISP)
	wisp2.play()
	assert wisp2.health == 1
	assert wisp2.atk == 1
	assert not wisp2.buffs


def test_end_turn_heal():
	game = prepare_game()

	footman = game.currentPlayer.give("CS1_042")
	footman.play()
	assert footman.health == 2
	game.endTurn()

	# play an archer on the footman
	archer = game.currentPlayer.give("CS2_189")
	archer.play(target=footman)
	assert footman.health == 1
	game.endTurn()

	healtotem = game.currentPlayer.give("NEW1_009")
	healtotem.play()
	game.endTurn()
	assert footman.health == 2
	game.endTurn()
	game.endTurn()
	# check it's still at max health after a couple of turns
	assert footman.health == 2


def test_crazed_alchemist():
	game = prepare_game()
	alchemist = game.currentPlayer.give("EX1_059")
	warden = game.currentPlayer.summon("EX1_396")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	assert warden.atk == 1
	assert warden.health == 7
	alchemist.play(target=warden)
	assert warden.atk == 7
	assert warden.health == 1


def test_conceal():
	game = prepare_game()
	conceal = game.currentPlayer.give("EX1_128")
	wisp1 = game.currentPlayer.give(WISP)
	wisp1.play()
	wisp2 = game.currentPlayer.give(WISP)
	wisp2.play()
	conceal.play()
	assert wisp1.stealthed
	assert wisp2.stealthed
	game.endTurn()
	assert wisp1.stealthed
	assert wisp2.stealthed
	game.endTurn()
	assert not wisp1.stealthed
	assert not wisp2.stealthed


def test_cruel_taskmaster():
	game = prepare_game()
	taskmaster1 = game.currentPlayer.give("EX1_603")
	taskmaster2 = game.currentPlayer.give("EX1_603")
	game.endTurn(); game.endTurn()

	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	taskmaster1.play(target=wisp)
	assert wisp.zone == Zone.GRAVEYARD
	game.endTurn(); game.endTurn()

	assert taskmaster1.health == 2
	assert taskmaster1.atk == 2
	taskmaster2.play(target=taskmaster1)
	assert taskmaster1.health == 1
	assert taskmaster1.atk == 4


def test_demolisher():
	game = prepare_game()

	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	demolisher = game.currentPlayer.give("EX1_102")
	demolisher.play()

	assert game.currentPlayer.opponent.hero.health == 30
	game.endTurn()
	assert game.currentPlayer.opponent.hero.health == 30
	game.endTurn()
	assert game.currentPlayer.opponent.hero.health == 28


def test_dread_infernal():
	game = prepare_game()
	infernal =  game.currentPlayer.give("CS2_064")
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	game.endTurn()
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	assert len(game.board) == 6
	infernal.play()
	assert len(game.board) == 1
	assert game.currentPlayer.hero.health == 29
	assert game.currentPlayer.opponent.hero.health == 29
	assert infernal.health == 6


def test_druid_of_the_fang():
	game = prepare_game()
	druid = game.currentPlayer.give("GVG_080")
	druid2 = game.currentPlayer.give("GVG_080")
	assert druid.id == druid2.id == "GVG_080"
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	druid.play()
	assert druid.id == "GVG_080"
	assert druid.atk == 4
	assert druid.health == 4

	game.endTurn(); game.endTurn()
	webspinner = game.currentPlayer.give("FP1_011")
	webspinner.play()
	druid2.play()
	assert druid2.id == "GVG_080t"
	assert druid2.atk == 7
	assert druid2.health == 7
	assert druid2.race == Race.BEAST


def test_imp_master():
	game = prepare_game()

	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	impmaster = game.currentPlayer.give("EX1_597")
	impmaster.play()

	assert impmaster.health == 5
	assert len(impmaster.controller.field) == 1
	game.endTurn()
	assert impmaster.health == 4
	assert len(impmaster.controller.field) == 2
	assert impmaster.controller.field.contains("EX1_598")


def test_auras():
	game = prepare_game()

	wisp1 = game.currentPlayer.give(WISP)
	wisp1.play()
	assert wisp1.atk == 1
	game.endTurn()

	# pass next few turns to gain some mana
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	webspinner = game.currentPlayer.give("FP1_011")
	webspinner.play()
	raidleader = game.currentPlayer.give("CS2_122")
	raidleader.play()
	assert raidleader.aura
	assert raidleader.atk == 2
	assert wisp1.atk == 1
	assert webspinner.atk == 2
	wisp2 = game.currentPlayer.give(WISP)
	wisp2.play()
	assert webspinner.atk == 2

	# Test the timber wolf (beast-only) too
	game.currentPlayer.getById(THE_COIN).play()
	timberwolf = game.currentPlayer.give("DS1_175")
	timberwolf.play()
	assert timberwolf.atk == 2 # 1 (+1 from RL)
	assert raidleader.atk == 2 # 2 (+0)
	assert len(webspinner.slots) == 2
	assert webspinner.atk == 3 # 1 (+1 from RL, +1 from TW)
	assert wisp2.atk == 2 # 1 (+1 from TW)


def test_bounce():
	game = prepare_game()
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	assert game.currentPlayer.field == [wisp]
	game.endTurn(); game.endTurn()

	brewmaster = game.currentPlayer.give("EX1_049")
	brewmaster.play(target=wisp)
	assert game.currentPlayer.field == [brewmaster]
	assert wisp in game.currentPlayer.hand
	assert wisp.zone == Zone.HAND
	wisp.play()
	game.endTurn(); game.endTurn()

	# test for damage reset on bounce
	brewmaster2 = game.currentPlayer.give("EX1_049")
	moonfire = game.currentPlayer.give(MOONFIRE)
	moonfire.play(target=brewmaster)
	assert brewmaster.health == 1
	brewmaster2.play(target=brewmaster)
	assert brewmaster.health == 2
	assert brewmaster2.health == 2

	game.endTurn()
	# fill the hand with some bananas
	game.currentPlayer.give("EX1_014t")
	game.currentPlayer.give("EX1_014t")
	game.endTurn()
	vanish = game.currentPlayer.give("NEW1_004")
	vanish.play()
	assert brewmaster not in game.currentPlayer.opponent.hand


def test_arcane_explosion():
	game = prepare_game(MAGE, MAGE)
	# play some wisps
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	game.endTurn()

	arcanex = game.currentPlayer.give("CS2_025")
	assert len(game.currentPlayer.opponent.field) == 3
	arcanex.play()
	assert len(game.currentPlayer.opponent.field) == 0


def test_arcane_missiles():
	game = prepare_game()
	missiles = game.currentPlayer.give("EX1_277")
	missiles.play()
	assert game.currentPlayer.opponent.hero.health == 27


def test_power_overwhelming():
	game = prepare_game()
	power = game.currentPlayer.give("EX1_316")
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	power.play(target=wisp)
	assert wisp.atk == 5
	assert wisp.health == 5
	game.endTurn()
	assert wisp not in game.board


def test_questing_adventurer():
	game = prepare_game()
	adventurer = game.currentPlayer.give("EX1_044")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	adventurer.play()
	assert adventurer.atk == 2
	assert adventurer.health == 2
	game.currentPlayer.give(THE_COIN).play()
	assert adventurer.atk == 3
	assert adventurer.health == 3
	game.currentPlayer.give(THE_COIN).play()
	game.currentPlayer.give(THE_COIN).play()
	game.currentPlayer.give(THE_COIN).play()
	assert adventurer.atk == 6
	assert adventurer.health == 6


def test_voidcaller():
	game = prepare_game()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.currentPlayer.discardHand()
	voidcaller = game.currentPlayer.give("FP1_022")
	voidcaller.play()

	# give the player a Doomguard and a couple of wisps
	doomguard = game.currentPlayer.give("EX1_310")
	game.currentPlayer.give(WISP)
	game.currentPlayer.give(WISP)
	game.currentPlayer.give(WISP)
	assert len(game.currentPlayer.hand) == 4

	# sacrificial pact on the voidcaller, should summon the Doomguard w/o discards
	game.currentPlayer.give("NEW1_003").play(target=voidcaller)
	assert voidcaller.zone == Zone.GRAVEYARD
	assert doomguard.zone == Zone.PLAY
	assert doomguard.canAttack()
	assert len(game.currentPlayer.hand) == 3


def test_void_terror():
	game = prepare_game()
	terror1 = game.currentPlayer.give("EX1_304")
	terror2 = game.currentPlayer.give("EX1_304")
	terror3 = game.currentPlayer.give("EX1_304")
	power = game.currentPlayer.give("EX1_316")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	terror1.play()
	assert terror1.atk == 3
	assert terror1.health == 3
	game.endTurn(); game.endTurn()

	terror2.play()
	assert terror1.zone == Zone.GRAVEYARD
	assert terror2.atk == 3+3
	assert terror2.health == 3+3
	game.endTurn(); game.endTurn()

	power.play(target=terror2)
	assert terror2.health == 3+3+4
	assert terror2.atk == 3+3+4
	terror3.play()
	assert terror2.zone == Zone.GRAVEYARD
	assert terror3.atk == 3+3+3+4
	assert terror3.health == 3+3+3+4
	game.endTurn(); game.endTurn()
	assert terror3.zone == Zone.PLAY


def test_mana_addict():
	game = prepare_game()
	manaaddict = game.currentPlayer.give("EX1_055")
	game.endTurn(); game.endTurn()

	manaaddict.play()
	assert manaaddict.atk == 1
	game.endTurn()

	assert manaaddict.atk == 1
	game.currentPlayer.give(THE_COIN).play()
	assert manaaddict.atk == 1
	game.endTurn()

	game.currentPlayer.give(THE_COIN).play()
	assert manaaddict.atk == 3
	game.currentPlayer.give(THE_COIN).play()
	assert manaaddict.atk == 5
	game.endTurn()
	assert manaaddict.atk == 1


def test_betrayal():
	game = prepare_game()
	betrayal = game.currentPlayer.give("EX1_126")
	game.endTurn(); game.endTurn()

	wisp1 = game.currentPlayer.give(WISP)
	wisp1.play()
	wisp2 = game.currentPlayer.give(WISP)
	wisp2.play()
	wisp3 = game.currentPlayer.give(WISP)
	wisp3.play()
	assert len(game.currentPlayer.field) == 3
	betrayal.play(target=wisp2)
	assert len(game.currentPlayer.field) == 1
	assert wisp1.zone == Zone.GRAVEYARD
	assert wisp2.zone == Zone.PLAY
	assert wisp3.zone == Zone.GRAVEYARD
	game.endTurn(); game.endTurn()

	bender = game.currentPlayer.give(SPELLBENDERT)
	bender.play()
	game.currentPlayer.give("EX1_126").play(target=wisp2)
	assert wisp2.zone == Zone.PLAY
	assert bender.zone == Zone.PLAY
	assert bender.health == 2
	bender.destroy(); wisp2.destroy()
	assert not game.currentPlayer.field
	game.endTurn(); game.endTurn()

	# prepare the board: two War Golems and an Emperor Cobra in the middle
	golem1 = game.currentPlayer.summon("CS2_186")
	cobra = game.currentPlayer.summon("EX1_170")
	golem2 = game.currentPlayer.summon("CS2_186")
	game.currentPlayer.give("EX1_126").play(target=cobra)

	assert golem1.zone == Zone.GRAVEYARD
	assert cobra.zone == Zone.PLAY
	assert golem2.zone == Zone.GRAVEYARD


def test_cold_blood():
	game = prepare_game()
	cb1 = game.currentPlayer.give("CS2_073")
	cb2 = game.currentPlayer.give("CS2_073")
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	game.endTurn(); game.endTurn()

	assert wisp.atk == 1
	cb1.play(target=wisp)
	assert wisp.atk == 1+2
	cb2.play(target=wisp)
	assert wisp.atk == 1+2+4


def test_corruption():
	game = prepare_game()
	corruption1 = game.currentPlayer.give("CS2_063")
	cabal = game.currentPlayer.give("EX1_091")
	game.endTurn()
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	wisp2 = game.currentPlayer.give(WISP)
	wisp2.play()
	corruption2 = game.currentPlayer.give("CS2_063")
	game.endTurn()

	corruption1.play(target=wisp)
	assert wisp.zone == Zone.PLAY
	assert wisp.buffs
	assert wisp.buffs[0].controller == game.currentPlayer
	game.endTurn()
	assert wisp.zone == Zone.PLAY
	game.endTurn()

	assert wisp.zone == Zone.GRAVEYARD
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn()

	# corrupt our own wisp. next turn opponent MCs it.
	corruption2.play(target=wisp2)
	assert wisp2.zone == Zone.PLAY
	game.endTurn()

	assert wisp2.zone == Zone.PLAY
	cabal.play(target=wisp2)
	assert wisp2.zone == Zone.PLAY
	game.endTurn()
	assert wisp2.zone == Zone.GRAVEYARD


def test_heroic_strike():
	game = prepare_game()
	strike = game.currentPlayer.give("CS2_105")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	assert game.currentPlayer.hero.atk == 0
	strike.play()
	assert game.currentPlayer.hero.atk == 4
	game.endTurn()
	assert game.currentPlayer.hero.atk == 0
	game.endTurn()
	assert game.currentPlayer.hero.atk == 0

	game.currentPlayer.give("CS2_105").play()
	game.currentPlayer.give("CS2_106").play()
	assert game.currentPlayer.hero.atk == 7


def test_humility():
	game = prepare_game()
	humility = game.currentPlayer.give("EX1_360")
	humility2 = game.currentPlayer.give("EX1_360")
	seargent = game.currentPlayer.give("CS2_188")
	seargent2 = game.currentPlayer.give("CS2_188")
	golem = game.currentPlayer.summon("CS2_186")
	game.endTurn(); game.endTurn()

	assert golem.atk == 7
	humility.play(target=golem)
	assert golem.atk == 1
	seargent.play(target=golem)
	assert golem.atk == 3
	game.endTurn()
	assert golem.atk == 1
	game.endTurn()

	seargent2.play(target=golem)
	assert golem.atk == 3
	humility2.play(target=golem)
	assert golem.atk == 1
	game.endTurn()
	assert golem.atk == 1


def test_hunters_mark():
	game = prepare_game()
	token = game.currentPlayer.give(SPELLBENDERT)
	token.play()
	assert token.health == 3
	game.currentPlayer.give(MOONFIRE).play(target=token)
	assert token.health == 2
	mark = game.currentPlayer.give("CS2_084")
	mark.play(target=token)
	assert token.health == 1
	game.currentPlayer.give(SILENCE).play(target=token)
	assert token.health == 3


def test_mindgames():
	game = prepare_game(PRIEST, PRIEST)
	mindgames = game.currentPlayer.give("EX1_345")

	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	assert len(game.currentPlayer.field) == 0
	mindgames.play()
	assert len(game.currentPlayer.field) == 1
	assert game.currentPlayer.opponent.deck.contains(game.currentPlayer.field[0])


def test_mind_vision():
	game = prepare_game()
	# discard our hand, let's clean this.
	game.currentPlayer.discardHand()
	game.endTurn()

	# play mind vision, should give nothing
	assert len(game.currentPlayer.hand) == 6
	game.currentPlayer.give("CS2_003").play()
	assert len(game.currentPlayer.hand) == 6

	# opponent draws a card, coin mind vision should get that one card
	drawn = game.currentPlayer.opponent.draw()
	game.currentPlayer.getById(THE_COIN).play()
	game.currentPlayer.give("CS2_003").play()
	assert game.currentPlayer.hand[-1] == drawn[0]


def test_mirror_image():
	game = prepare_game()
	mirror = game.currentPlayer.give("CS2_027")
	mirror.play()
	assert len(game.currentPlayer.field) == 2
	assert game.currentPlayer.field[0].id == "CS2_mirror"
	assert game.currentPlayer.field[1].id == "CS2_mirror"


def test_archmage_antonidas():
	game = prepare_game()

	antonidas = game.currentPlayer.give("EX1_559")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	antonidas.play()
	game.currentPlayer.discardHand()
	assert len(game.currentPlayer.hand) == 0
	game.currentPlayer.give(MOONFIRE).play(target=game.currentPlayer.opponent.hero)
	assert len(game.currentPlayer.hand) == 1
	assert game.currentPlayer.hand[0].id == "CS2_029"
	game.currentPlayer.give(THE_COIN).play()
	assert len(game.currentPlayer.hand) == 2
	assert game.currentPlayer.hand[1].id == "CS2_029"


def test_armorsmith():
	game = prepare_game()
	game.endTurn(); game.endTurn()

	armorsmith1 = game.currentPlayer.give("EX1_402")
	armorsmith1.play()
	game.endTurn()
	armorsmith2 = game.currentPlayer.give("EX1_402")
	armorsmith2.play()
	game.endTurn()

	assert not game.currentPlayer.hero.armor
	armorsmith1.attack(target=armorsmith2)
	assert game.currentPlayer.hero.armor == 1
	assert game.currentPlayer.opponent.hero.armor == 1

	game.endTurn()
	game.currentPlayer.give("EX1_402").play()
	game.currentPlayer.give(WISP).play()

	# Whirlwind. 1 armor on each hero, 2 armorsmiths in play for current player, 1 for opponent.
	game.currentPlayer.give("EX1_400").play()
	assert game.currentPlayer.hero.armor == 7
	assert game.currentPlayer.hero.health == 30
	assert game.currentPlayer.opponent.hero.armor == 2


def test_blessing_of_wisdom():
	game = prepare_game()
	blessing = game.currentPlayer.give("EX1_363")
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	blessing.play(target=wisp)
	game.endTurn(); game.endTurn()

	game.currentPlayer.discardHand()
	wisp.attack(target=game.currentPlayer.opponent.hero)
	assert len(game.currentPlayer.hand) == 1
	game.endTurn(); game.endTurn()
	game.endTurn()

	shadowmadness = game.currentPlayer.give("EX1_334")
	shadowmadness.play(target=wisp)
	assert len(game.currentPlayer.opponent.hand) == 2
	game.currentPlayer.discardHand()
	wisp.attack(target=game.currentPlayer.opponent.hero)
	assert len(game.currentPlayer.opponent.hand) == 3
	assert not game.currentPlayer.hand


def test_baron_rivendare():
	game = prepare_game()
	gnome = game.currentPlayer.give("EX1_029")
	gnome.play()
	assert not gnome.extraDeathrattles
	rivendare = game.currentPlayer.summon("FP1_031")
	assert gnome.extraDeathrattles
	game.currentPlayer.give(MOONFIRE).play(target=gnome)
	assert game.currentPlayer.opponent.hero.health == 26
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	assert not wisp.hasDeathrattle
	sotf = game.currentPlayer.give("EX1_158")
	sotf.play()
	assert len(wisp.slots) == 2
	assert len(game.currentPlayer.field) == 2
	game.currentPlayer.give(MOONFIRE).play(target=wisp)
	assert wisp.zone == Zone.GRAVEYARD
	assert rivendare.zone == Zone.PLAY
	assert len(game.currentPlayer.field) == 3 # Rivendare and two treants
	rivendare.destroy()
	assert len(game.currentPlayer.field) == 3 # Only one treant spawns


def test_blood_knight():
	game = prepare_game()
	bloodknight1 = game.currentPlayer.give("EX1_590")
	bloodknight2 = game.currentPlayer.give("EX1_590")
	bloodknight3 = game.currentPlayer.give("EX1_590")
	game.endTurn(); game.endTurn()
	game.endTurn()

	squire = game.currentPlayer.give("EX1_008")
	squire.play()
	assert squire.divineShield
	game.endTurn()
	bloodknight1.play()
	assert not squire.divineShield
	assert bloodknight1.atk == 6
	assert bloodknight1.health == 6
	game.endTurn()
	game.currentPlayer.give("EX1_008").play()
	game.currentPlayer.give("EX1_008").play()
	# Play an argent protector on the squire
	game.currentPlayer.give("EX1_362").play(target=squire)
	assert squire.divineShield
	game.endTurn()
	bloodknight2.play()
	assert not squire.divineShield
	assert bloodknight2.atk == 12
	assert bloodknight2.health == 12
	game.endTurn(); game.endTurn()
	bloodknight3.play()
	assert bloodknight3.atk == 3
	assert bloodknight3.health == 3


def test_bolvar_fordragon():
	game = prepare_game()
	bolvar = game.currentPlayer.give("GVG_063")
	assert bolvar.atk == 1
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	game.currentPlayer.give(MOONFIRE).play(target=wisp)
	assert bolvar.atk == 2
	assert bolvar.buffs
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	game.currentPlayer.give(MOONFIRE).play(target=wisp)
	assert bolvar.atk == 3
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	assert bolvar.atk == 3
	assert bolvar.buffs
	bolvar.play()
	assert bolvar.atk == 3
	assert bolvar.buffs
	# game.currentPlayer.give(DREAM).play(target=bolvar)
	# assert bolvar.atk == 1
	# assert not bolvar.buffs


def test_defias():
	game = prepare_game()

	defias1 = game.currentPlayer.give("EX1_131")
	defias1.play()
	assert len(game.currentPlayer.field) == 1

	game.endTurn()

	# Coin-defias
	game.currentPlayer.getById(THE_COIN).play()
	defias2 = game.currentPlayer.give("EX1_131")
	defias2.play()
	assert len(game.currentPlayer.field) == 2


def test_doomsayer():
	game = prepare_game()

	# play some wisps
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()

	game.endTurn();
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()

	assert len(game.board) == 4
	doomsayer = game.currentPlayer.give("NEW1_021")
	doomsayer.play()
	assert len(game.board) == 5

	game.endTurn()
	assert len(game.board) == 5
	game.endTurn()
	assert len(game.board) == 0


def test_gadgetzan_auctioneer():
	game = prepare_game()

	game.currentPlayer.summon("EX1_095")
	assert len(game.currentPlayer.hand) == 4
	game.currentPlayer.give(MOONFIRE).play(target=game.currentPlayer.opponent.hero)
	assert len(game.currentPlayer.hand) == 5
	game.currentPlayer.give(WISP).play()
	assert len(game.currentPlayer.hand) == 5


def test_gahzrilla():
	game = prepare_game()
	gahz = game.currentPlayer.summon("GVG_049")
	assert gahz.atk == 6
	game.currentPlayer.give(MOONFIRE).play(target=gahz)
	assert gahz.atk == 6*2
	timberwolf = game.currentPlayer.give("DS1_175")
	timberwolf.play()
	assert gahz.atk == (6*2) + 1
	# TODO: Buffs are always taken into account at the end
	# game.currentPlayer.give(MOONFIRE).play(target=gahz)
	# assert gahz.atk == (6*2*2) + 1



def test_gruul():
	game = prepare_game()
	gruul = game.currentPlayer.summon("NEW1_038")
	assert gruul.atk == 7
	assert gruul.health == 7
	assert not gruul.buffs
	game.endTurn()
	assert gruul.buffs
	assert gruul.atk == 8
	assert gruul.health == 8
	game.endTurn()
	assert gruul.atk == 9
	assert gruul.health == 9


def test_hogger():
	game = prepare_game()
	hogger = game.currentPlayer.give("NEW1_040")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	hogger.play()
	assert len(game.currentPlayer.field) == 1
	game.endTurn()
	assert len(game.currentPlayer.opponent.field) == 2
	assert game.currentPlayer.opponent.field[1].id == "NEW1_040t"
	game.endTurn()
	assert len(game.currentPlayer.field) == 2
	game.endTurn()
	assert len(game.currentPlayer.opponent.field) == 3


def test_houndmaster():
	game = prepare_game()
	houndmaster = game.currentPlayer.give("DS1_070")
	hound = game.currentPlayer.give("EX1_538t")
	hound.play()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	assert hound.atk == 1
	assert hound.health == 1
	assert not hound.taunt
	houndmaster.play(target=hound)
	assert hound.atk == 3
	assert hound.health == 3
	assert hound.taunt


def test_illidan():
	game = prepare_game()
	illidan = game.currentPlayer.give("EX1_614")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	assert len(game.board) == 0
	illidan.play()
	assert len(game.board) == 1
	game.currentPlayer.give(MOONFIRE).play(target=illidan)
	assert len(game.board) == 2
	game.currentPlayer.give(MOONFIRE).play(target=illidan)
	assert len(game.board) == 3
	game.currentPlayer.give(MOONFIRE).play(target=illidan)
	assert len(game.board) == 4
	game.currentPlayer.give(MOONFIRE).play(target=illidan)
	assert len(game.board) == 5

	# 5th moonfire kills illidan, but spawns another token before
	game.currentPlayer.give(MOONFIRE).play(target=illidan)
	assert len(game.board) == 5
	assert illidan.zone == Zone.GRAVEYARD


def test_leeroy():
	game = prepare_game()
	leeroy = game.currentPlayer.give("EX1_116")

	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	leeroy.play()
	assert leeroy.canAttack()
	assert game.currentPlayer.opponent.field.contains("EX1_116t")
	assert game.currentPlayer.opponent.field[0] == game.currentPlayer.opponent.field[1]


def test_lorewalker_cho():
	game = prepare_game()
	cho = game.currentPlayer.give("EX1_100")
	game.endTurn(); game.endTurn()

	cho.play()
	game.currentPlayer.discardHand()
	game.currentPlayer.opponent.discardHand()
	assert len(game.currentPlayer.hand) == 0
	assert len(game.currentPlayer.opponent.hand) == 0
	game.currentPlayer.give(THE_COIN).play()
	assert len(game.currentPlayer.hand) == 0
	assert len(game.currentPlayer.opponent.hand) == 1
	assert game.currentPlayer.opponent.hand[0].id == THE_COIN

	game.endTurn()
	game.currentPlayer.discardHand()
	game.currentPlayer.give(THE_COIN).play()
	assert len(game.currentPlayer.hand) == 0
	assert len(game.currentPlayer.opponent.hand) == 1
	assert game.currentPlayer.opponent.hand[0].id == THE_COIN
	game.currentPlayer.give(THE_COIN).play()


def test_lightspawn():
	game = prepare_game()
	lightspawn = game.currentPlayer.give("EX1_335")
	flametongue = game.currentPlayer.give("EX1_565")

	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	lightspawn.play()
	assert lightspawn.health == 5
	assert lightspawn.atk == 5

	game.endTurn()
	# play archer on lightspawn, goes to 4 health
	game.currentPlayer.give("CS2_189").play(target=lightspawn)
	assert lightspawn.health == 4
	assert lightspawn.atk == 4
	assert not lightspawn.buffs
	game.endTurn(); game.endTurn()
	flametongue.play()

	assert lightspawn.health == 4
	assert lightspawn.buffs
	assert lightspawn.atk == 4

	game.currentPlayer.give(SILENCE).play(target=lightspawn)
	# 2 attack from the flametongue
	assert lightspawn.atk == 2


def test_lightwarden():
	game = prepare_game(PRIEST, PRIEST)
	lightwarden = game.currentPlayer.give("EX1_001")
	lightwarden.play()
	assert lightwarden.atk == 1
	game.endTurn(); game.endTurn();

	# No-op heal should not do anything.
	assert game.currentPlayer.hero.health == 30
	game.currentPlayer.hero.power.play(target=game.currentPlayer.hero)
	assert game.currentPlayer.hero.health == 30
	assert lightwarden.atk == 1
	lightwarden.attack(target=game.currentPlayer.opponent.hero)
	game.endTurn()
	game.currentPlayer.hero.power.play(target=game.currentPlayer.hero)
	assert lightwarden.atk == 3


def test_lightwell():
	game = prepare_game()
	lightwell = game.currentPlayer.give("EX1_341")

	game.endTurn(); game.endTurn()
	game.currentPlayer.give(MOONFIRE).play(target=game.currentPlayer.hero)
	game.currentPlayer.give(MOONFIRE).play(target=game.currentPlayer.opponent.hero)
	lightwell.play()
	assert game.currentPlayer.hero.health == 29
	assert game.currentPlayer.opponent.hero.health == 29
	game.endTurn()
	assert game.currentPlayer.opponent.hero.health == 29
	assert game.currentPlayer.hero.health == 29
	game.endTurn()
	assert game.currentPlayer.hero.health == 30
	assert game.currentPlayer.opponent.hero.health == 29


def test_molten_giant():
	game = prepare_game()
	molten = game.currentPlayer.give("EX1_620")
	assert molten.cost == 20
	game.currentPlayer.give(MOONFIRE).play(target=game.currentPlayer.hero)
	assert molten.cost == 19
	game.currentPlayer.give(MOONFIRE).play(target=game.currentPlayer.hero)
	assert molten.cost == 18
	game.currentPlayer.give(MOONFIRE).play(target=game.currentPlayer.hero)
	assert molten.cost == 17
	game.endTurn()

	assert molten.cost == 17
	molten2 = game.currentPlayer.give("EX1_620")
	assert molten2.cost == 20


def test_mountain_giant():
	game = prepare_game()
	mountain = game.currentPlayer.give("EX1_105")
	assert mountain.baseCost == 12
	assert mountain.cost == 12 - len(game.currentPlayer.hand) + 1
	game.endTurn(); game.endTurn()
	assert mountain.cost == 12 - len(game.currentPlayer.hand) + 1
	game.endTurn(); game.endTurn()
	assert mountain.cost == 12 - len(game.currentPlayer.hand) + 1


def test_sea_giant():
	game = prepare_game()
	seagiant = game.currentPlayer.give("EX1_586")
	assert seagiant.baseCost == 10
	assert seagiant.cost == 10
	game.currentPlayer.give(WISP).play()
	assert seagiant.cost == 9
	game.currentPlayer.give(WISP).play()
	assert seagiant.cost == 8
	game.currentPlayer.give(WISP).play()
	assert seagiant.cost == 7
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	assert seagiant.cost == 3
	game.endTurn()
	for i in range(7):
		game.currentPlayer.give(WISP).play()
	assert seagiant.cost == 0


def test_murloc_tidecaller():
	game = prepare_game()
	tidecaller = game.currentPlayer.give("EX1_509")
	tidecaller.play()
	assert tidecaller.atk == 1
	game.endTurn()
	game.currentPlayer.give("CS2_168").play()
	assert tidecaller.atk == 2
	game.endTurn()
	# Play a tidehunter. Summons two murlocs.
	game.currentPlayer.give("EX1_506").play()
	assert tidecaller.atk == 4


def test_nortshire_cleric():
	game = prepare_game(PRIEST, PRIEST)
	cleric = game.currentPlayer.give("CS2_235")
	cleric.play()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.currentPlayer.discardHand()
	assert not game.currentPlayer.hand
	game.currentPlayer.hero.power.play(target=game.currentPlayer.hero)
	assert not game.currentPlayer.hand
	pyro = game.currentPlayer.give("NEW1_020")
	pyro.play()
	game.currentPlayer.give(CIRCLE_OF_HEALING).play()
	assert not game.currentPlayer.hand
	game.currentPlayer.give(CIRCLE_OF_HEALING).play()
	assert len(game.currentPlayer.hand) == 2
	game.currentPlayer.give(CIRCLE_OF_HEALING).play()
	assert len(game.currentPlayer.hand) == 4


def test_ragnaros():
	game = prepare_game()
	ragnaros = game.currentPlayer.give("EX1_298")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	ragnaros.play()
	assert not ragnaros.canAttack()
	assert game.currentPlayer.opponent.hero.health == 30
	game.endTurn()

	assert game.currentPlayer.hero.health == 22
	game.endTurn()

	assert game.currentPlayer.opponent.hero.health == 22
	assert not ragnaros.canAttack()


def test_truesilver_champion():
	game = prepare_game()
	truesilver = game.currentPlayer.give("CS2_097")
	lightwarden = game.currentPlayer.give("EX1_001")
	lightwarden.play()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	truesilver.play()
	assert game.currentPlayer.hero.weapon is truesilver
	assert game.currentPlayer.hero.atk == 4
	assert game.currentPlayer.hero.health == 30
	game.currentPlayer.hero.attack(target=game.currentPlayer.opponent.hero)
	assert game.currentPlayer.hero.health == 30
	assert lightwarden.atk == 1
	game.endTurn(); game.endTurn()
	game.currentPlayer.give(MOONFIRE).play(target=game.currentPlayer.hero)
	game.currentPlayer.give(MOONFIRE).play(target=game.currentPlayer.hero)
	game.currentPlayer.give(MOONFIRE).play(target=game.currentPlayer.hero)
	game.currentPlayer.hero.attack(target=game.currentPlayer.opponent.hero)
	assert game.currentPlayer.hero.health == 29
	assert lightwarden.atk == 3



def test_twilight_drake():
	game = prepare_game()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	assert len(game.currentPlayer.hand) == 7
	drake = game.currentPlayer.give("EX1_043")
	drake.play()
	assert len(game.currentPlayer.hand) == 7
	assert drake.health == 1+7
	assert drake.buffs

	game.endTurn()
	game.currentPlayer.discardHand()
	drake2 = game.currentPlayer.give("EX1_043")
	assert len(game.currentPlayer.hand) == 1
	drake2.play()
	assert not game.currentPlayer.hand
	assert drake2.health == 1
	assert not drake2.buffs


def test_unbound_elemental():
	game = prepare_game()
	unbound = game.currentPlayer.give("EX1_258")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	unbound.play()
	assert unbound.atk == 2
	assert unbound.health == 4
	game.currentPlayer.give(THE_COIN).play()
	assert unbound.atk == 2
	assert unbound.health == 4
	# Lightning Bolt should trigger it
	game.currentPlayer.give("EX1_238").play(target=game.currentPlayer.opponent.hero)
	assert unbound.atk == 3
	assert unbound.health == 5
	game.endTurn()
	game.currentPlayer.give("EX1_238").play(target=game.currentPlayer.opponent.hero)
	assert unbound.atk == 3
	assert unbound.health == 5


def test_undertaker():
	game = prepare_game()
	undertaker = game.currentPlayer.give("FP1_028")
	undertaker.play()
	game.currentPlayer.give(WISP).play()
	assert not undertaker.buffs
	assert undertaker.atk == 1
	assert undertaker.health == 2
	game.endTurn()

	# Play a leper gnome, should not trigger undertaker
	game.currentPlayer.give("EX1_029").play()
	assert undertaker.atk == 1
	assert undertaker.health == 2
	game.endTurn()

	game.currentPlayer.give("EX1_029").play()
	assert undertaker.atk == 2
	assert undertaker.health == 3

	game.currentPlayer.give("EX1_029").play()
	assert undertaker.atk == 3
	assert undertaker.health == 4


def test_vancleef():
	game = prepare_game()
	vancleef1 = game.currentPlayer.give("EX1_613")
	vancleef2 = game.currentPlayer.give("EX1_613")
	game.endTurn(); game.endTurn()

	assert not game.currentPlayer.cardsPlayedThisTurn
	game.currentPlayer.give(THE_COIN).play()
	game.currentPlayer.give(THE_COIN).play()
	game.currentPlayer.give(THE_COIN).play()
	game.currentPlayer.give(THE_COIN).play()
	game.currentPlayer.give(THE_COIN).play()
	assert game.currentPlayer.cardsPlayedThisTurn == 5
	vancleef1.play()
	assert game.currentPlayer.cardsPlayedThisTurn == 6
	assert vancleef1.atk == 12
	assert vancleef1.health == 12
	game.endTurn(); game.endTurn()

	assert not game.currentPlayer.cardsPlayedThisTurn
	vancleef2.play()
	assert game.currentPlayer.cardsPlayedThisTurn == 1
	assert vancleef2.atk == 2
	assert vancleef2.health == 2


def test_wild_pyromancer():
	game = prepare_game()
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	pyro = game.currentPlayer.give("NEW1_020")
	game.endTurn(); game.endTurn()

	pyro.play()
	assert pyro.health == 2
	assert wisp.zone == Zone.PLAY

	# play moonfire. wisp should die.
	game.currentPlayer.give(MOONFIRE).play(target=game.currentPlayer.opponent.hero)
	assert wisp.zone == Zone.GRAVEYARD
	assert pyro.health == 1

	# play circle of healing. pyro should go up to 2hp then back to 1.
	game.currentPlayer.give(CIRCLE_OF_HEALING).play()
	assert pyro.health == 1
	assert pyro.zone == Zone.PLAY

	# Silence the pyromancer. It should not trigger.
	game.currentPlayer.give(SILENCE).play(target=pyro)
	assert pyro.health == 1
	assert pyro.zone == Zone.PLAY


def test_shadow_madness_wild_pyro():
	game = prepare_game()
	pyro = game.currentPlayer.give("NEW1_020")
	game.endTurn(); game.endTurn()

	pyro.play()
	game.endTurn()
	game.endTurn(); game.endTurn()

	assert pyro.controller == game.player1
	assert pyro in game.player1.field
	assert pyro.health == 2
	shadowmadness = game.currentPlayer.give("EX1_334")
	shadowmadness.play(target=pyro)
	assert pyro.controller == game.player2
	assert pyro in game.player2.field
	assert pyro.health == 1
	game.endTurn()
	assert pyro.controller == game.player1
	assert pyro in game.player1.field


def test_shadow_madness_silence():
	game = prepare_game()
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn()

	assert wisp.controller == game.player1
	shadowmadness = game.currentPlayer.give("EX1_334")
	shadowmadness.play(target=wisp)
	assert wisp.controller == game.player2
	game.currentPlayer.give(SILENCE).play(target=wisp)
	assert wisp.controller == game.player1
	game.endTurn()
	assert wisp.controller == game.player1


def test_shadowform():
	game = prepare_game(PRIEST, PRIEST)
	shadowform1 = game.currentPlayer.give("EX1_625")
	shadowform2 = game.currentPlayer.give("EX1_625")
	shadowform3 = game.currentPlayer.give("EX1_625")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	# Hero Power should reset
	assert game.currentPlayer.hero.power.id == "CS1h_001"
	assert game.currentPlayer.hero.power.isPlayable()
	game.currentPlayer.hero.power.play(target=game.currentPlayer.hero)
	assert not game.currentPlayer.hero.power.isPlayable()
	assert shadowform1.isPlayable()
	shadowform1.play()
	assert game.currentPlayer.hero.power.id == "EX1_625t"
	assert game.currentPlayer.hero.power.isPlayable()
	game.currentPlayer.hero.power.play(target=game.currentPlayer.opponent.hero)
	assert not game.currentPlayer.hero.power.isPlayable()
	assert game.currentPlayer.opponent.hero.health == 28
	game.endTurn(); game.endTurn()

	shadowform2.play()
	assert game.currentPlayer.hero.power.id == "EX1_625t2"
	assert game.currentPlayer.hero.power.isPlayable()
	game.currentPlayer.hero.power.play(target=game.currentPlayer.opponent.hero)
	assert not game.currentPlayer.hero.power.isPlayable()
	assert game.currentPlayer.opponent.hero.health == 25

	shadowform3.play()
	assert game.currentPlayer.hero.power.id == "EX1_625t2"
	assert not game.currentPlayer.hero.power.isPlayable()


def test_acolyte_of_pain():
	game = prepare_game()
	acolyte = game.currentPlayer.give("EX1_007")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	assert len(game.currentPlayer.hand) == 7
	acolyte.play()
	assert len(game.currentPlayer.hand) == 6
	game.currentPlayer.give(MOONFIRE).play(target=acolyte)
	assert len(game.currentPlayer.hand) == 7
	game.currentPlayer.give(MOONFIRE).play(target=acolyte)
	assert len(game.currentPlayer.hand) == 8
	game.currentPlayer.give(MOONFIRE).play(target=acolyte)
	assert len(game.currentPlayer.hand) == 9
	assert acolyte.zone == Zone.GRAVEYARD


def test_poisonous():
	game = prepare_game()
	game.endTurn(); game.endTurn()
	game.endTurn()
	game.currentPlayer.getById(THE_COIN).play()
	cobra = game.currentPlayer.give("EX1_170")
	cobra.play()
	assert cobra.poisonous
	game.endTurn()
	zchow = game.currentPlayer.give("FP1_001")
	zchow.play()
	zchow2 = game.currentPlayer.give("FP1_001")
	zchow2.play()
	game.endTurn()
	cobra.attack(target=zchow)
	assert zchow not in game.currentPlayer.opponent.field
	assert zchow.zone == Zone.GRAVEYARD
	game.endTurn()
	zchow2.attack(target=cobra)
	assert zchow2.zone == Zone.GRAVEYARD

	# test silencing the cobra
	zchow3 = game.currentPlayer.give("FP1_001")
	zchow3.play()
	game.endTurn()
	cobra = game.currentPlayer.give("EX1_170")
	cobra.play()
	cobra.silence()
	game.endTurn()
	zchow3.attack(cobra)
	assert zchow3 in game.currentPlayer.field
	assert cobra in game.currentPlayer.opponent.field


def test_cleave():
	game = prepare_game()
	# play some wisps
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	game.endTurn()

	# Play the coin
	game.currentPlayer.getById(THE_COIN).play()

	cleave = game.currentPlayer.give("CS2_114")
	assert cleave.isPlayable()
	cleave.play()
	assert len(game.currentPlayer.opponent.field) == 0

	# play another wisp
	game.currentPlayer.give(WISP).play()

	game.endTurn()
	cleave2 = game.currentPlayer.give("CS2_114")
	assert not cleave2.isPlayable()


def test_upgrade():
	game = prepare_game()
	axe = game.currentPlayer.give("CS2_106")
	upgrade = game.currentPlayer.give("EX1_409")
	game.endTurn(); game.endTurn()
	axe.play()
	game.currentPlayer.hero.attack(game.currentPlayer.opponent.hero)
	assert game.currentPlayer.opponent.hero.health == 27

	game.endTurn()
	upgrade2 = game.currentPlayer.give("EX1_409")
	upgrade2.play()
	assert game.currentPlayer.hero.atk == 1
	assert game.currentPlayer.hero.weapon.atk == 1
	game.endTurn()
	assert game.currentPlayer.hero.weapon.atk == 3
	assert game.currentPlayer.hero.weapon.durability == 1
	upgrade.play()
	assert game.currentPlayer.hero.weapon.atk == 4
	assert game.currentPlayer.hero.weapon.durability == 2
	game.currentPlayer.hero.attack(game.currentPlayer.opponent.hero)
	assert game.currentPlayer.opponent.hero.health == 23
	assert game.currentPlayer.hero.weapon.durability == 1

	# test Bloodsail Corsair
	game.endTurn()
	corsair = game.currentPlayer.give("NEW1_025")
	corsair.play()
	assert axe.zone == Zone.GRAVEYARD
	assert not game.currentPlayer.opponent.hero.weapon


CHEAT_MIRROR_ENTITY = True
def test_mctech():
	game = prepare_game()
	game.endTurn(); game.endTurn()
	game.endTurn()
	# play some wisps
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	game.currentPlayer.give(WISP).play()
	# coin mirror entity
	game.currentPlayer.getById(THE_COIN).play()
	if CHEAT_MIRROR_ENTITY:
		# TODO secrets
		game.currentPlayer.give("EX1_294").play()
	game.endTurn()

	assert len(game.currentPlayer.opponent.field) == 3
	# play an mctech. nothing should be controlled.
	game.currentPlayer.give("EX1_085").play()
	assert len(game.currentPlayer.field) == 1
	game.endTurn()
	if CHEAT_MIRROR_ENTITY:
		# mc tech gets copied, board now at 4
		game.currentPlayer.give("EX1_085").play()
	assert len(game.currentPlayer.field) == 4
	game.endTurn()
	game.currentPlayer.give("EX1_085").play()
	assert len(game.currentPlayer.field) == 3
	assert len(game.currentPlayer.opponent.field) == 3


def test_inner_fire():
	game = prepare_game()
	innerfire = game.currentPlayer.give("CS1_129")
	seargent = game.currentPlayer.give("CS2_188")
	gurubashi = game.currentPlayer.summon("EX1_399")
	game.endTurn(); game.endTurn()
	assert gurubashi.atk == 2
	seargent.play(target=gurubashi)
	assert gurubashi.atk == 4
	innerfire.play(target=gurubashi)
	assert gurubashi.atk == 7
	game.endTurn(); game.endTurn()
	assert gurubashi.atk == 7


def test_ice_barrier():
	game = prepare_game(MAGE, MAGE)
	icebarrier = game.currentPlayer.give("EX1_289")
	icebarrier2 = game.currentPlayer.give("EX1_289")
	friendlywisp = game.currentPlayer.give(WISP)
	friendlywisp.play()
	game.endTurn()
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	wisp2 = game.currentPlayer.give(WISP)
	wisp2.play()
	game.endTurn()
	game.endTurn(); game.endTurn()

	assert icebarrier.isPlayable()
	icebarrier.play()
	assert not icebarrier2.isPlayable()
	assert game.currentPlayer.secrets
	assert icebarrier in game.currentPlayer.secrets
	assert not game.currentPlayer.hero.armor
	game.endTurn(); game.endTurn()

	assert not icebarrier2.isPlayable()
	friendlywisp.attack(target=game.currentPlayer.opponent.hero)
	assert not game.currentPlayer.hero.armor
	assert not game.currentPlayer.opponent.hero.armor
	game.endTurn(); game.endTurn()

	friendlywisp.attack(target=wisp2)
	assert not game.currentPlayer.hero.armor
	assert not game.currentPlayer.opponent.hero.armor
	assert friendlywisp.zone == Zone.GRAVEYARD
	assert wisp2.zone == Zone.GRAVEYARD
	game.endTurn()

	assert len(game.currentPlayer.opponent.secrets) == 1
	wisp.attack(target=game.currentPlayer.opponent.hero)
	assert not game.currentPlayer.opponent.secrets
	assert game.currentPlayer.opponent.hero.armor == 7


def test_vaporize():
	game = prepare_game()
	vaporize = game.currentPlayer.give("EX1_594")
	game.endTurn()
	wisp = game.currentPlayer.give(WISP)
	wisp.play()
	game.endTurn()
	game.endTurn(); game.endTurn()
	vaporize.play()
	assert game.currentPlayer.secrets[0] == vaporize
	game.endTurn()
	assert len(game.currentPlayer.opponent.secrets) == 1
	# Play an axe and hit the hero ourselves
	game.currentPlayer.give("CS2_106").play()
	game.currentPlayer.hero.attack(target=game.currentPlayer.opponent.hero)
	assert len(game.currentPlayer.opponent.secrets) == 1
	assert game.currentPlayer.opponent.hero.health == 27
	wisp.attack(target=game.currentPlayer.opponent.hero)
	assert not game.currentPlayer.opponent.secrets
	assert vaporize.zone == Zone.GRAVEYARD
	assert wisp.zone == Zone.GRAVEYARD
	assert game.currentPlayer.opponent.hero.health == 27


def test_stoneskin_gargoyle():
	game = prepare_game()
	gargoyle = game.currentPlayer.give("FP1_027")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()
	gargoyle.play()
	assert gargoyle.health == 4
	# damage the gargoyle by 1
	game.currentPlayer.give(MOONFIRE).play(target=gargoyle)
	assert gargoyle.health == 3
	game.endTurn(); game.endTurn()
	assert gargoyle.health == 4

	# soulpriest test. NYI
	# soulpriest = game.currentPlayer.give("EX1_591")
	# soulpriest.play()
	# game.endTurn(); game.endTurn()
	# assert gargoyle.health == 4
	# game.currentPlayer.give(MOONFIRE).play(target=gargoyle)
	# assert gargoyle.health == 3
	# game.endTurn(); game.endTurn()
	# assert gargoyle.health == 2
	# game.endTurn(); game.endTurn()
	# assert gargoyle.zone == Zone.GRAVEYARD


def test_sunfury_protector():
	game = prepare_game()
	sunfury = game.currentPlayer.give("EX1_058")
	game.endTurn(); game.endTurn()

	wisp1 = game.currentPlayer.give(WISP)
	wisp1.play()
	wisp2 = game.currentPlayer.give(WISP)
	wisp2.play()
	sunfury.play()
	assert not wisp1.taunt
	assert wisp2.taunt


def test_faerie_dragon():
	game = prepare_game(MAGE, MAGE)
	dragon = game.currentPlayer.give("NEW1_023")
	game.endTurn(); game.endTurn()
	game.endTurn(); game.endTurn()

	dragon.play()
	moonfire = game.currentPlayer.give(MOONFIRE)
	assert dragon not in moonfire.targets
	assert dragon not in game.currentPlayer.hero.power.targets
	game.endTurn()

	assert dragon not in game.currentPlayer.hero.power.targets
	archer = game.currentPlayer.give("CS2_189")
	assert dragon in archer.targets



def test_flare():
	game = prepare_game(HUNTER, HUNTER)
	flare = game.currentPlayer.give("EX1_544")
	worgen = game.currentPlayer.give("EX1_010")
	worgen.play()
	game.endTurn()

	avenge = game.currentPlayer.give("FP1_020")
	avenge.play()
	game.endTurn()

	flare.play()
	assert not game.currentPlayer.opponent.secrets
	assert not worgen.stealthed


def test_warlock():
	game = prepare_game(WARLOCK, WARLOCK)
	sacpact = game.currentPlayer.give("NEW1_003")
	assert not sacpact.isPlayable()
	flameimp = game.currentPlayer.give("EX1_319")
	flameimp.play()
	assert game.currentPlayer.hero.health == 27
	assert sacpact.isPlayable()
	sacpact.play(target=flameimp)
	assert game.currentPlayer.hero.health == 30
	game.endTurn()


def main():
	for name, f in globals().items():
		if name.startswith("test_") and hasattr(f, "__call__"):
			f()
	print("All tests ran OK")


if __name__ == "__main__":
	main()
