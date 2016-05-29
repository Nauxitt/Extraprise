from engine import Room
import items


class Room_brig(Room):
	name = "the brig"
	description = "There's a bunch of switches and stuff"

	def __init__(self):
		super().__init__()
		self.go = {
			'north':  Room_hallway_01,
		}
		self.westcount = 0
		self.captain_here = True

	def onEnter(self):
		# If re-entering room, 50% chance of
		# seeing the captain again.
		if not self.captain_here:
			self.captain_here = (random() >= 0.5)
		
		if self.captain_here:
			name = self.world.name
			print("The captain enters.")
			print('"Greetings, %s, your name is %s.  How are you?"' % (name, name))
			howareyou = input(' ": ')
			print('"%s," eh?  Good to hear!' % howareyou)
			print("The captain leaves...")
			self.captain_here = 0
	
	def command(self, cmd):
		# If you go west a bunch of times in a row, you win.
		# This class doesn't consider "go west" to be
		# a valid command, though, so you get the default
		# message upon walking into walls.
		if cmd == 'go west':
			self.westcount += 1
			if self.westcount >= 7:
				winGame()
			return False
		else:
			self.westcount = 0
		return False


class Room_hallway_00(Room):
	description = "It's just a boring old hall."
	name = "a hallway"

	def __init__(self):
		super().__init__()
		self.go = {
			'south': Room_brig,
			'north': Room_hallway_02,
		}

	def onEnter(self):
		print("You successfully go somewhere else")
		pass


class Room_hallway_01(Room):
	description = "It's a hall.  Well, it would be if you remembered what a hall was.  You don't.  It is not a hall."
	name = "more hall"

	def __init__(self):
		super().__init__()
		self.go = {
			'south': Room_hallway_01,
			'east': Room_gunroom,
		}


class Room_gunroom(Room):
	description = "The room before you is as cold as the cell, though the walls are a pale fuschia. In the center, sits a table. It looks like it could bear a fairly heavy load, but you wouldn't be confident standing on it."

	def __init__(self):
		super().__init__()
		self.go = {
			'west': Room_hallway_01,
		}
		
		self.objects = {
			items.Gun(): 'A gun lays on the table.',
		}

	def command(self, cmd):
		if cmd == 'stand on table':
			print("It collapses.  Your confidence, that is.  The table is otherwise unharmed.")
			self.world['confidence'] -= 1
			return True
