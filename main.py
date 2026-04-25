"""Punto de entrada del videojuego 2D."""

from game.game import Game


def main() -> None:
	game = Game()
	game.run()


if __name__ == "__main__":
	main()
