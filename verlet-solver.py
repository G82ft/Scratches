from tkinter import Tk, Canvas, Frame, Button, Checkbutton, IntVar, Scale, Menu, BooleanVar
from time import time, sleep
from threading import Thread


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

    def __eq__(self, other):
        if not isinstance(other, Vector):
            raise TypeError

        return self.values == other.values

    def copy(self):
        return Vector(self.values.copy())

    @property
    def values(self):
        return self._values.copy()

    @property
    def length(self):
        f, s = self.values
        return (f ** 2 + s ** 2) ** 0.5


ZERO_VECTOR = Vector([0, 0])


class VerletObject:
    def __init__(self, position: Vector, radius: int, is_static: bool, color: str = 'white'):
        self.position: Vector = position.copy()
        self.position_old: Vector = position.copy()

        self.radius: int = radius
        self.is_static: bool = is_static
        self.color: str = color

        self.acceleration = ZERO_VECTOR.copy()

    def __eq__(self, other):
        if not isinstance(other, VerletObject):
            raise TypeError

        return all(
            (
                s == o for s, o in (
                    (self.position, other.position),
                    (self.radius, other.radius),
                    (self.is_static, other.is_static),
                    (self.color, other.color),
                )
            )
        )

    def update_position(self, dt: int) -> None:
        velocity: Vector = self.position - self.position_old

        self.position_old = self.position.copy()

        self.position = self.position + velocity + self.acceleration * dt * dt

        self.acceleration = ZERO_VECTOR.copy()

    def accelerate(self, acc: Vector):
        self.acceleration += acc

    def get_coords(self):
        rel_coords = Vector(
            [
                self.radius,
                self.radius
            ]
        )
        ld = self.position - rel_coords
        ru = self.position + rel_coords

        return ld.values + ru.values


class Link:
    def __init__(self, objects: tuple[VerletObject, VerletObject], length: float, is_fixed: bool = True):
        self.objects: tuple[VerletObject, VerletObject] = objects
        self.length: float = length
        self.is_fixed: bool = is_fixed

    def update(self):
        obj1, obj2 = self.objects

        axis: Vector = obj1.position - obj2.position
        dist: float = axis.length

        if self.is_fixed or dist > self.length:
            n: Vector = axis / dist
            d: float = (self.length - dist) / 100
            if not obj1.is_static:
                obj1.position += n * d
            if not obj2.is_static:
                obj2.position -= n * d

    def get_coords(self):
        return [i for obj in self.objects for i in obj.position]


class Constraint:
    def __init__(self, radius: float, position: Vector):
        self.radius: float = radius
        self.position: Vector = position

    def apply(self, obj: VerletObject) -> None:
        to_obj: Vector = obj.position - self.position
        dist: float = to_obj.length

        if dist > (self.radius - obj.radius):
            n: Vector = to_obj / dist
            obj.position = self.position + n * (self.radius - obj.radius)

    def get_coords(self):
        rel_coords: Vector = Vector(
            [
                self.radius,
                self.radius
            ]
        )
        ld = self.position - rel_coords
        ru = self.position + rel_coords

        return ld.values + ru.values


class Solver:
    def __init__(
            self,
            sub_steps: int = 1,
            constraint: Constraint = None, canvas: Canvas = None,
            gravity: Vector = Vector([0, 1000])
    ):
        if sub_steps <= 0:
            sub_steps = 1
        self.sub_steps: int = sub_steps

        self.constraint: Constraint = constraint
        self.canvas: Canvas = canvas
        self.gravity: Vector = gravity.copy()

        self.objects: dict[int: VerletObject] = {}
        self.links: dict = {}

    def update(self, dt: float) -> None:
        dt /= self.sub_steps

        for _ in range(self.sub_steps):

            for id, obj in self.objects.items():
                if obj.is_static:
                    continue

                obj.accelerate(self.gravity)
                obj.update_position(dt)
                if self.constraint is not None:
                    self.constraint.apply(obj)

                for obj2 in self.objects.values():
                    collision_axis: Vector = obj.position - obj2.position
                    dist: float = collision_axis.length
                    min_dist = obj.radius + obj2.radius
                    if dist < min_dist and dist != 0:
                        n: Vector = collision_axis / dist
                        d: float = (min_dist - dist) / 2
                        if not obj.is_static:
                            obj.position += n * d
                        if not obj2.is_static:
                            obj2.position -= n * d

            for L in self.links.values():
                L.update()

    def draw(self):
        for id, obj in self.objects.items():
            rel_coords: Vector = Vector(
                [
                    obj.radius,
                    obj.radius
                ]
            )
            self.canvas.moveto(id, *obj.position - rel_coords)

        links = self.links.copy()

        for id in links.keys():
            self.canvas.delete(id)
            line = self.links.pop(id)

            id = self.canvas.create_line(*line.get_coords(), fill='grey')

            self.links[id] = line

    def add_obj(self, obj: VerletObject):
        id = self.canvas.create_oval(
            *obj.get_coords(),
            fill=obj.color
        )
        self.objects[id] = obj

    def remove_obj(self, id):
        if id in self.objects:
            del self.objects[id]
            self.canvas.delete(id)

    def add_link(self, link: Link):
        id = self.canvas.create_line(
            *link.get_coords(),
            fill='grey'
        )

        for i in link.objects:
            if i not in self.objects.values():
                self.add_obj(i)

        self.links[id] = link


class Root:
    def __init__(self, solver: Solver = Solver(), fps: int = 30, *args, **kwargs):
        if fps <= 0:
            fps = 1
        self.fps: int = fps

        self.solver = solver
        self.root = Tk(*args, **kwargs)

        self.root.columnconfigure(0, weight=1)
        for i in range(2):
            self.root.rowconfigure(0, weight=1)
        self.root.geometry('750x750')
        self.root.resizable(False, False)

        canvas = Canvas(self.root)
        canvas.grid(row=0, column=0, sticky='nesw')
        self.solver.canvas = canvas

        self.fps_counter = self.solver.canvas.create_text(
            15,
            10,
            text=f'{fps}',
            justify='left'
        )

        if self.solver.constraint is not None:
            canvas.create_oval(*self.solver.constraint.get_coords(), fill='black')

        self.menu_opened: bool = False

        # Bindings
        canvas.bind(
            '<ButtonRelease-1>',
            lambda e: self.solver.add_obj(
                VerletObject(
                    Vector(
                        [
                            e.x,
                            e.y
                        ]
                    ),
                    self.obj_size.get(),
                    self.obj_is_static.get()
                )
            ) if not self.menu_opened else self.close_menu(self.solver.canvas.find_closest(e.x, e.y)[0])
        )
        canvas.bind(
            '<ButtonRelease-2>',
            lambda e: self.solver.remove_obj(
                e.widget.find_closest(e.x, e.y)[0]
            )
        )

        self.linked_obj_id: int = None
        canvas.bind(
            '<ButtonRelease-3>',
            self.summon_object_menu
        )

        canvas.bind(
            '<Control-Motion>',
            self.drag_obj
        )

        # Frame with actions
        f: Frame = Frame(
            self.root,
            relief='ridge',
            bd=10
        )
        for i in range(3):
            f.columnconfigure(i, weight=1)
        f.grid(row=2, column=0,
               sticky='nesw')

        self.obj_is_static: BooleanVar = BooleanVar()
        Checkbutton(
            f,
            text='Static',
            variable=self.obj_is_static
        ).grid(row=0, column=0)

        self.obj_size: IntVar = IntVar()
        Scale(
            f,
            label='Size',
            from_=1,
            to=100,
            orient='horizontal',
            variable=self.obj_size
        ).grid(row=0, column=1)
        self.link_length: IntVar = IntVar()
        Scale(
            f,
            label='Link size',
            from_=1,
            to=1000,
            orient='horizontal',
            variable=self.link_length
        ).grid(row=0, column=2,
               sticky='ew')

    def summon_object_menu(self, event):
        self.menu_opened = True
        solver: Solver = self.solver
        canvas: Canvas = self.solver.canvas

        obj_id: int = canvas.find_closest(event.x, event.y)[0]
        if obj_id not in solver.objects:
            return None
        canvas.itemconfig(obj_id, outline='red')

        m: Menu = Menu(tearoff=False)
        m.add_command(label="Remove", command=lambda: self.remove(obj_id), accelerator=f'{obj_id}')
        is_static: BooleanVar = BooleanVar()
        is_static.set(solver.objects[obj_id].is_static)
        m.add_checkbutton(label='Static', command=lambda: self.change_state(obj_id), variable=is_static)
        m.add_command(label='Link', accelerator=f'{self.linked_obj_id}', command=lambda: self.link_objs(obj_id))

        m.post(self.root.winfo_x() + event.x, self.root.winfo_y() + event.y)

    def remove(self, obj_id: int):
        self.solver.remove_obj(obj_id)

        self.close_menu(obj_id)

    def change_state(self, obj_id: int):
        obj = self.solver.objects[obj_id]
        obj.is_static = not obj.is_static

        self.close_menu(obj_id)

    def link_objs(self, obj_id: int):
        if self.linked_obj_id is None:
            self.linked_obj_id = obj_id
        else:
            self.solver.add_link(
                Link(
                    (self.solver.objects[self.linked_obj_id], self.solver.objects[obj_id]),
                    self.link_length.get(),
                    False
                )
            )

            self.close_menu(obj_id)
            self.close_menu(self.linked_obj_id)

            self.linked_obj_id = None

    def close_menu(self, obj_id: int):
        self.solver.canvas.itemconfig(obj_id, outline='black')
        self.menu_opened = False

    def drag_obj(self, event):
        solver: Solver = self.solver
        canvas: Canvas = self.solver.canvas

        obj_id = canvas.find_closest(event.x, event.y)[0]
        if obj_id not in solver.objects:
            return None

        obj = solver.objects[obj_id]
        obj.is_static = True
        obj.position = Vector(
            [event.x, event.y]
        )

    def mainloop(self):
        i = 0
        while True:
            start = time()

            t = Thread(target=sleep, args=(1 / self.fps,))
            t.start()

            self.root.update()
            self.root.update_idletasks()

            self.solver.draw()

            t.join()

            end = time()

            if i % 10 == 0 and (end - start) != 0:
                self.solver.canvas.itemconfig(self.fps_counter, text=f'{round(1 / (end - start), 1)}')
            i += 1

            self.solver.update(1 / self.fps)


con = Constraint(325, Vector([375, 335]))
solver = Solver(8, con)
root = Root(solver, 60)

root.mainloop()
