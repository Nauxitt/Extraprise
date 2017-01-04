from re import compile as rgx


class World(object):
	'''
		Convenient game-container class in case I
		want to reuse this trash.
		
		The main use is to provide a container for
		all game data and general game interactions.

		It indexes instances of room
		objects by their classes, allowing these room
		classes to keep track of the rooms they link to
		simply by storing pointers to the class.

		It also provides a centeral structure of every
		GameObject.
	'''
	def __init__(self):
		self.location = None
		self.rooms = {}
		self.prompt = ' > '
		self.autolook = False
		self.vars = {}

		self.objects = {}
		self.inventory = Container(world=self)
		
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
			r = self.rooms[room] = room(world=self)
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
	
	def prompt_command(self, raw):
		if raw.startswith(':'):
			self.on_debug_command(raw[1:])
		com = Command(raw)
		self.command(com)
	
	def on_debug_command(self, cmd):
		if cmd == 'room':
			print(self.location)
		else:
			print("Debug command %s not found" % cmd.action)
		
	def command(self, cmd):
		loc_cmd_exit = self.location.command(cmd)

		if loc_cmd_exit:
			return True

		if cmd.action in ['go', 'g']:
			direction = cmd.target
			r = self.enterRoom(
				self.location.go.get(direction, None)
			)
			if r is None:
				print("No.")
			return True

		elif cmd.action in ['look', 'l']:
			if cmd.target:
				target = self.target(cmd.target)
				if target:
					print(target.description)
				else:
					print(cmd.target+"?")
			else:
				self.location.onLook()
			return True

		elif cmd.action == 'autolook':
			self.autolook = not self.autolook
			print(
				"Autolook turned",
				"ON" if self.autolook else "OFF"
			)
			return True

		elif cmd.action in ['inventory', 'inv', 'i']:
			items = {}
			for obj in self.inventory:
				id = obj.__class__()
				if obj.typename:
					id = obj.typename

				if id in items:
					items[id] += 1
				else:
					items[id] = 1

			for obj, quantity in items.items():
				print("%sx - %s" % (quantity, obj))

			return True

		target = self.target(cmd.target)
		if target:
			if cmd.action == 'take':
				if target.takable:
					print("You've taken the", cmd.target)
					target.moveTo(self.inventory)
				else:
					print("No.")
				return True

			result = target.targetedCommand(cmd)
			if result:
				return result
			
			for obj in self.inventory:
				result = obj.command(cmd)
				if result:
					return True
		else:
			for obj in self.commandHandlers():
				result = obj.command(cmd)
				if result:
					return result

		return False
	
	def commandHandlers(self):
		for obj in self.location:
			yield obj

		for obj in self.inventory:
			yield obj

		yield self.location
	
	def target(self, target):
		for obj in self.location:
			if target in obj.names:
				return obj
		for obj in self.inventory:
			if target in obj.names:
				return obj
		return None
	
	def gameLoop(self, ):
		while True:
			for obj in self.objects.values():
				obj.tick()
			self.location.tick()
			self.prompt_command(input(self.prompt))
	
	def startGame(self):
		self.intro()
		self.gameLoop()
	
	def spawn(self, objClass, *args, **kwargs):
		obj = objClass()
		obj.id = len(self.objects)
		obj.world = self
		self.objects[obj.id] = obj
		return obj


class Container(object):
	def __init__(self, container=None, world=None):
		self.container = container
		self.world = world
		self.objects = {}
	
	def __iter__(self):
		return iter(self.objects.values())
		
	def spawn(self, objClass, *args, **kwargs):
		if self.world:
			obj = self.world.spawn(objClass, *args, **kwargs)
		else:
			obj = objClass()
			obj.id = len(self.objects)
			obj.world = self.world
		self.add(obj)
		return obj

	def add(self, obj):
		self.objects[obj.id] = obj
		obj.container = self

	def remove(self, obj):
		o = self.objects.get(obj.id, None)
		o.container = None
		if isinstance(obj, GameObject):
			del self.objects[obj.id]
		else:
			del self.objects[obj]
		return o


class Room(Container):
	description = None
	name = None

	def __init__(self, world=None):
		self.go = {}
		self.world = world
		super().__init__(world=world, container=self)

	def onEnter(self):
		pass
	
	def onLook(self):
		if self.description:
			desc = [self.description]
			for obj in self.objects.values():
				if obj.location_description:
					desc.append(obj.location_description)
				elif obj.location_description:
					desc.append(obj.description)
			print(" ".join(desc))

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
	
	def tick(self):
		pass


class Command(object):
	def __init__(self, raw):
		words = raw.split(" ")

		# TODO: special parsing for words like "the"
		
		action = words.pop(0)
		preposition, target, object_used = [None] * 3

		if len(words) == 1:
			# Used for verb-target commands like "take captain" or "eat self"
			target = words[0]
		elif len(words) == 2:
			# For commands like "stand on table" or "look inside soul"
			preposition, target = words
		elif len(words) == 3:
			# Used for commands like "take cat from bag"
			# Certain prepositions allow for special parsing, such as
			# "Shoot captain using gun" or "fill bag with cat"
			
			object_used, preposition, target = words
			if preposition in ['with', 'using']:
				object_used, target = target, object_used

		self.action = action
		
		# TODO: convert preposition to an ideal synonym
		self.preposition = preposition

		self.target = target
		self.object_used = object_used
		self.raw = raw
	
	def match(self, action=None, target=None, object_used=None, preposition=None):
		if action and self.action != action:
			return False
		if target and self.target != target:
			return False
		if preposition and self.preposition != preposition:
			return False
		if object_used and self.object_used != object_used:
			return False
		return True


class GameObject(object):
	typename = None
	world = None
	description = None
	location_description = None
	pronouns = ['it']
	takable = False

	def __init__(self, location_description=None, description=None):
		if self.location_description:
			if location_description:
				self.location_description = location_description
		else:
			self.location_description = location_description

		if self.description:
			if description:
				self.description = description
		else:
			self.description = description
	
	def targetedCommand(self, cmd):
		return False
	
	def command(self, cmd):
		return False
	
	def moveTo(self, target):
		if self.container:
			self.container.remove(self)

		if isinstance(target, dict):
			target[self.id] = self
		elif isinstance(target, Container):
			target.add(self)

	def tick(self):
		pass
