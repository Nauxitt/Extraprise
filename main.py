import sys
from engine import World

# TODO: Add confidence check at some point.

# This game needs to suck, so all prints are capitalized.
#ProperTechnique
'''
import builtins
__oldprint = print
def print(*args, **kwargs):
	__oldprint((" ".join(map(str, args)).upper()), **kwargs)
builtins.print = print
'''


def winGame():
	print("Gratz, you won!")
	input()
	sys.exit(1)


class Game(World):
	def intro(self):
		print("You wake up on the steel floor. Of the brig. Of the starship Extraprise.  You have no memories, not even language.  Not even the starship you're on, or what a starship is.")
		print()
		print("Assuming you could understand this question, and assuming you could remember how to speak the answer, what would your name be, if you were to remember it?")

		self.name = input(" > ")

		if self.name == 'dikfuk':
			print("Welcome, Dongsmasher")
			print("(Enter 'win' at any time to... eh... win.)")
		self['confidence'] = 1

		from rooms import Room_brig
		self.enterRoom(Room_brig)
	
	def command(self, cmd):
		if cmd.action == 'win':
			if self.name == 'dikfuk':
				winGame()
			else:
				print("No.")
			return True
		elif cmd.action == 'yes':
			print('No.')
		elif cmd.action == 'no':
			print('Yes.')

		return super().command(cmd)

game = None


def main():
	game = Game()
	game.startGame()

if __name__ == "__main__":
	main()
