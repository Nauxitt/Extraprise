from re import compile as rgx


class World(object):
	'''
		Convenient game-container class in case I
		want to reuse this trash.

		It's main use is to index instances of room
		objects by their classes, allowing these room
		classes to keep track of the rooms they link to
		simply by storing pointers to the classes.
	'''
	def __init__(self):
		self.location = None
		self.rooms = {}
		self.prompt = ' > '
		self.autolook = False
		self.vars = {}

		# TODO: make this do nifty, CLI-game v2.0 things
		self.aliases = {
			rgx('[^\sgo]+n$'): 'go north',
			rgx('[^\sgo]+e$'): 'go east',
			rgx('[^\sgo]+s$'): 'go south',
			rgx('[^\sgo]+w$'): 'go west',
			rgx('[^\sgo]+g\s+'): 'go ',

			rgx('^l$'): 'look',
		}
	
	def __getitem__(self, attr):
		return self.vars[attr]
	
	def __setitem__(self, attr, val):
		self.vars[attr] = val

	def enterRoom(self, room):
		'''
			Give it a Room class instance, and it'll
			send the player to that room, initializing
			an instance of the room's class if needed.

			Returns the room instance, or None if no
			room is found.
		'''
		if room is None:
			return None

		r = self.rooms.get(room, None)
		if r is None:
			r = self.rooms[room] = room()
			r.world = self

		self.location = r
		if self.autolook:
			r.onLook()
		r.onEnter()
		return r
	
	def intro(self):
		'''
			Method that gets fired at the start of game.
		'''
		pass
	
	def command(self, inpt):
		inpt = inpt.strip().lower()
		loc_cmd_exit = self.location.command(inpt)

		if loc_cmd_exit:
			return False

		words = inpt.split(" ")
		cmd = words[0]

		if cmd == 'go':
			direction = words[1]
			r = self.enterRoom(
				self.location.go.get(direction, None)
			)
			if r is None:
				print("No.")
			return True
		elif cmd == 'look':
			self.location.onLook()
			return True
		elif cmd == 'autolook':
			self.autolook = not self.autolook
			print(
				"Autolook turned",
				"ON" if self.autolook else "OFF"
			)
		return False
	
	def startGame(self):
		self.intro()
		while True:
			self.command(input(self.prompt))


class Room(object):
	description = None
	name = None

	def __init__(self):
		self.go = {}
		self.world = None

	def onEnter(self):
		pass
	
	def onLook(self):
		if self.description:
			print(self.description)

		for direction, place in self.go.items():
			if place.name:
				print(direction+":\t"+place.name)
	
	def command(self, cmd):
		'''
			If you subclass Room, you can give it custom
			command interpretation.
			A return of False signifies this method didn't
			know what to do with it's input, so go with
			whatever defaults the game engine wants.
		'''
		return False


class Item(object):
	pass
