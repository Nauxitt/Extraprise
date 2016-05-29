from engine import Item


class Gun(Item):
	takable = True
	desc = "It's a gun, jackass. You know what it looks like. Got that?"
	
	def command(self, cmd):
		words = cmd.split(" ")
		command = words[0]
		if command == 'shoot':
			# TODO: shoot something
			return True
		return False
