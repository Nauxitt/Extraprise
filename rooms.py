from engine import Room, GameObject
from random import random
from main import winGame


class Room_brig(Room):
	name = "the brig"
	description = "You are in the brig."

	class Captain(GameObject):
		names = ['captain']
		pronouns = ['them', 'he', 'her']
		WAIT_TIME = 3
		location_description = "The captain is here."

		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			self.wait = self.WAIT_TIME

		def tick(self):
			if self.container == self.world.location:
				if self.wait:
					self.wait -= 1
				else:
					self.container.remove(self)
					print("The captain leaves...")
			else:
				self.wait = self.WAIT_TIME
	
		def yap(self):
			name = self.world.name
			print("The captain enters.")
			print('"Greetings, %s, your name is %s.  How are you?"' % (name, name))
			howareyou = input(' ": ')
			print('"%s," eh?  Good to hear!' % howareyou)

	class Switches(GameObject):
		names = ["switch", "switches", "button", "buttons"]
		pronouns = ['them']
		description = "You don't know what they are, or what they do. Perhaps you should aimlessly experiement with them?"
		location_description = "There's a bunch of switches and buttons and stuff."
		
		def targetedCommand(self, cmd):
			if cmd.action in ["push"]:
				if cmd.target == "switch":
					print("Pushing a switch is a dumb idea.")
				elif cmd.target == "button":
					print("You pick a button at random and push it.  The ship has exploded.")
					winGame()
				return True

			if cmd.action in ['flip']:
				if cmd.target == "button":
					print("You can't flip a button, dumbass.")
				if cmd.target == "switch":
					# TODO: something
					print("Nothing happens. Maybe the #gamedev hasn't added it yet.")
				return True
			return False

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.go = {
			'north':  Room_hallway_00,
		}
		self.westcount = 0
		self.captain_here = True
		
		self.spawn(self.Switches)
		self.captain = self.spawn(self.Captain)
		self.captain_yapped = False

	def onEnter(self):
		# If re-entering room, 50% chance of
		# seeing the captain again.
		if not self.captain_yapped:
			self.captain.yap()
			self.captain_yapped = True
		elif self.captain not in self:
			if random() >= 0.5:
				self.captain.moveTo(self)
				self.captain.yap()
	
	def command(self, cmd):
		# If you go west a bunch of times in a row, you win.
		# This class doesn't consider "go west" to be
		# a valid command, though, so you get the default
		# message upon walking into walls, concealing the feature.
		if cmd.match('go', 'west'):
			self.westcount += 1
			if self.westcount >= 7:
				winGame()
		else:
			self.westcount = 0

		return False


class Room_hallway_00(Room):
	description = "It's just a boring old hall."
	name = "a hallway"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.go = {
			'south': Room_brig,
			'north': Room_hallway_01,
		}

	def onEnter(self):
		print("You successfully go somewhere else")
		pass


class Room_hallway_01(Room):
	description = "It's a hall.  Well, it would be if you remembered what a hall was.  You don't.  It is not a hall."
	name = "more hall"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.go = {
			'south': Room_hallway_00,
			'east': Room_gunroom,
		}


class Room_gunroom(Room):
	description = "The room before you is as cold as the cell, though the walls are a pale fuschia. In the center, sits a table. It looks like it could bear a fairly heavy load, but you wouldn't be confident standing on it."
	name = "Gun Room"

	class Gun(GameObject):
		typename = "Gun"
		names = ["gun"]
		takable = True
		description = "It's a gun, jackass. You know what it looks like. Got that?"

		def command(self, cmd):
			if cmd.action == 'shoot':
				if cmd.target:
					target = self.world.target(cmd.target)
					if target:
						print("Pew.")
					else:
						print("You try to shoot something that isn't there. You hit nothing, so in a sense you succeed.")
				else:
					print("You fire the gun into the wall.")
				return True
			return False

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.go = {
			'west': Room_hallway_01,
		}
		
		self.spawn(
			self.Gun,
			location_description = "Speaking of load, a gun lays on the table."
		)

	def command(self, cmd):
		if cmd.match('stand', 'table'):
			print("It collapses.  Your confidence, that is.  The table is otherwise unharmed.")
			self.world['confidence'] -= 1
			return True
