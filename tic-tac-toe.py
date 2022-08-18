import tkinter
from tkinter import Tk, Frame, Label, Button, StringVar
from tkinter.font import Font
from tkinter.messagebox import showinfo
from time import sleep
from threading import Thread

WINS: list = [
    [
        [True] * 3,
        [False] * 3,
        [False] * 3
    ],
    [
        [False] * 3,
        [True] * 3,
        [False] * 3
    ],
    [
        [False] * 3,
        [False] * 3,
        [True] * 3
    ],
    [
        [True, False, False]
    ] * 3,
    [
        [False, True, False]
    ] * 3,
    [
        [False, False, True]
    ] * 3,
    [
        [True, False, False],
        [False, True, False],
        [False, False, True]
    ],
    [
        [False, False, True],
        [False, True, False],
        [True, False, False]
    ]
]


def flash(element) -> None:
    def _flash(element):
        for _ in range(2):
            element["bg"] = 'pink'
            sleep(0.25)
            element["bg"] = '#d9d9d9'
            sleep(0.25)

    Thread(target=_flash, args=(element,)).start()

    return None


class Root:
    def __init__(self):
        self.root = Tk()
        self.root.title("Tic-tac-toe")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        f = Frame(
            self.root
        )
        f.grid(sticky='nesw')

        self.labels: list = [[None for _ in range(3)] for _ in range(3)]
        self.buttons: list = [[None for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                var = StringVar()
                var.set(' ')
                self.labels[i][j] = var
                self.buttons[i][j] = Button(
                    f,
                    textvariable=var,
                    font=Font(font=('Droid Sans Mono', 20)),
                    bd=5,
                    command=lambda x=i, y=j: self.handle_turn(x, y)
                )
                self.buttons[i][j].grid(column=i, row=j, sticky='')
                f.columnconfigure(i, weight=1)
                f.rowconfigure(j, weight=1)

        self.turn = StringVar()
        self.turn.set('×')

        Label(
            self.root,
            text=' ',
            textvariable=self.turn,
            font=Font(font=('Droid Sans Mono', 20))
        ).grid(column=0, row=1)

    def handle_turn(self, column: int, row: int):
        if self.labels[column][row].get() != ' ':
            flash(self.buttons[column][row])
            return None

        turn = self.turn.get()
        self.labels[column][row].set(turn)

        bin_field: list = [
                [
                    r.get() == turn
                    for r in c
                ]
                for c in self.labels
        ]

        if (
            [True, True, True] in bin_field
            or [True, True, True] in [[r[i] for r in bin_field] for i in range(3)]
            or all(bin_field[i][i] for i in range(3))
            or all(bin_field[i][2-i] for i in range(3))
        ):
            showinfo('Info', f'{turn} wins!')
            self.root.destroy()

        self.turn.set('o' if self.turn.get() == '×' else '×')


Root().root.mainloop()
