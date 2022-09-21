from math import copysign
from random import uniform
from time import sleep
from tkinter import Tk, Canvas


class Vector:
    def __init__(self, values: list):
        self._values: list = list(values)

    def __str__(self):
        return 'Vector({}, {})'.format(*self.values)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, index):
        return self.values.__getitem__(index)

    def __setitem__(self, index, value):
        return self._values.__setitem__(index, value)

    def __iter__(self):
        return self._values.__iter__()

    def __mul__(self, other):
        result = self.copy()

        if not isinstance(other, (int, float)):
            raise TypeError

        for i in range(2):
            result[i] *= other

        return result

    def __truediv__(self, other):
        result = self.copy()

        if not isinstance(other, (int, float)):
            raise TypeError

        for i in range(2):
            result[i] /= other

        return result

    def __floordiv__(self, other):
        result = self.copy()

        if not isinstance(other, (int, float)):
            raise TypeError

        for i in range(2):
            result[i] //= other

        return result

    def __pow__(self, power):
        result = self.copy()

        if not isinstance(power, (int, float)):
            raise TypeError

        for i in range(2):
            result[i] **= power

        return result

    def __add__(self, other):
        result = self.copy()

        if not isinstance(other, Vector):
            raise TypeError

        for i in range(2):
            result[i] += other.values[i]

        return result

    def __sub__(self, other):
        result = self.copy()

        if not isinstance(other, Vector):
            raise TypeError

        for i in range(2):
            result[i] -= other.values[i]

        return result

    def copy(self):
        return Vector(self.values.copy())

    @property
    def values(self):
        return self._values.copy()

    @property
    def length(self):
        f, s = self.values
        return (f ** 2 + s ** 2) ** 0.5

    @property
    def direction(self):
        return self / self.length


class Player:
    def __init__(self, size: Vector, axis: float):
        self.size: Vector = size

        self.axis: float = axis
        self._position: float = 0.0

    def get_coords(self):
        center = self.size / 2
        ld = self.position - center
        ru = self.position + center

        return ld.values + ru.values

    def is_colliding(self, ball) -> bool:
        x_size, y_size = self.size
        x, y = ball.position
        xb_size = ball.size[0]

        return (
                self.axis - x_size - xb_size < x < self.axis + x_size + xb_size
                and self._position - y_size < y < self._position + self.size[1]
        )

    def move(self, y, max_: int = 500):
        if self.size[1] / 2 < y < max_ - self.size[1] / 2:
            self._position = 10 * (y // 10)

    @property
    def position(self):
        return Vector(
            [
                self.axis - self.size[0] // 2,
                self._position - self.size[1] / 2
            ]
        )


class Ball:
    def __init__(self, size):
        self.size: Vector = Vector(
            [
                size, size
            ]
        )

        self.velocity: Vector = Vector(
            [
                0, 0
            ]
        )
        self.position: Vector = Vector(
            [
                500, 250
            ]
        )

    def update(self, difficulty: int = 10):
        self.position = self.position + self.velocity * difficulty

    def bounce_of_wall(self):
        self.velocity[1] *= -1
        self.velocity[0] = uniform(0, copysign(1, self.velocity[0]))

    def bounce_of_player(self):
        self.velocity[0] *= -1
        self.velocity[1] = uniform(-1, 1)

    def get_coords(self):
        center = self.size / 2
        ld = self.position - center
        ru = self.position + center

        return ld.values + ru.values

    @property
    def screen_position(self):
        return ((self.position - (self.size / 2)) // 10) * 10


class Game:
    def __init__(self, x, y):
        self.x, self.y = x, y

        self.root = Tk()
        self.root.resizable(False, False)
        self.root.geometry(f'{x}x{y}')
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.screen = Canvas(self.root)
        self.screen.grid(
            row=0, column=0,
            sticky='nesw'
        )
        self.screen.create_rectangle(0, 0, x, y, fill='#000')

        self.ball: Ball = Ball(10)
        self.ball_id: int = self.screen.create_rectangle(*self.ball.get_coords(), fill='#000', outline='#fff')
        self.ball.velocity[1] = 0
        self.ball.velocity[0] = -1

        self.left_player: Player = Player(
            Vector([10, 50]), 20
        )
        self.lp_id: int = self.screen.create_rectangle(*self.left_player.get_coords(), fill='#000', outline='#fff')
        self.lp_score: int = 0
        self.lp_score_id: int = self.screen.create_text(x // 2 - 10, 15, text=0, fill='#fff')

        self.right_player: Player = Player(
            Vector([10, 50]), self.x - 20
        )
        self.rp_id: int = self.screen.create_rectangle(*self.right_player.get_coords(), fill='#000', outline='#fff')
        self.rp_score: int = 0
        self.rp_score_id: int = self.screen.create_text(x // 2 + 10, 15, text=0, fill='#fff')

        self.difficulty: int = 1

        self.screen.bind('<Motion>', lambda e: self.right_player.move(e.y, self.y))
        self.screen.bind_all('<KeyPress-Down>', lambda e: self.right_player.move(self.right_player._position + 20, self.y))
        self.screen.bind_all('<KeyPress-Up>', lambda e: self.right_player.move(self.right_player._position - 20, self.y))

    def mainloop(self):
        while True:
            sleep(1 / 60)
            self.root.update()
            self.root.update_idletasks()

            self.ball.update(self.difficulty + self.lp_score + self.rp_score)
            self.screen.moveto(self.ball_id, *self.ball.screen_position.values)

            if not (self.ball.size[1] < self.ball.position[1] < self.y - self.ball.size[1]):
                self.ball.bounce_of_wall()

            self.left_player.move(self.ball.position[1], self.y)
            self.screen.moveto(self.lp_id, *self.left_player.position)
            self.screen.moveto(self.rp_id, *self.right_player.position)

            for player in (self.left_player, self.right_player):
                if player.is_colliding(self.ball):
                    self.ball.bounce_of_player()
                    self.difficulty += 1

            if not (0 < self.ball.position[0] < self.x):
                if self.ball.position[0] < 0:
                    self.lp_score += 1
                else:
                    self.rp_score += 1

                self.screen.itemconfig(self.lp_score_id, text=self.lp_score)
                self.screen.itemconfig(self.rp_score_id, text=self.rp_score)

                self.ball.position = Vector(
                    [
                        self.x / 2,
                        self.y / 2
                    ]
                )
                self.ball.velocity = Vector(
                    [
                        uniform(-1, 1),
                        uniform(-1, 1)
                    ]
                )


Game(1000, 500).mainloop()
