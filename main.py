from dataclasses import dataclass
import abc as ABC
from typing import Optional


@dataclass
class Roll:
    pins: int

class Frame(ABC):
    def __init__(self):
        self.rolls: list[Roll] = []
        self._next_frame: Optional[Frame] = None

    @property
    def next_frame(self):
        return self._next_frame

    @next_frame.setter
    def next_frame(self, value):
        self._next_frame = value
    @property
    def total_pins(self):
        return sum(roll.pins for roll in self.rolls)

    def is_strike(self) -> bool:
        return self.rolls[0].pins == 10

    def is_spare(self) -> bool:
        if len(self.rolls) == 2:
            return self.rolls[0].pins + self.rolls[1].pins == 10

    @ABC.abstractmethod
    def add_roll(self, pins: int):
        raise NotImplementedError
    @ABC.abstractmethod
    def score(self) -> int:
        raise NotImplementedError

class NormalFrame(Frame):

    def __init__(self):
        super().__init__()

    def add_roll(self, pins: int):
        if pins + self.total_pins > 10:
            raise ValueError("A frame's rolls cannot exceed 10 pins")
        if len(self.rolls) < 2:
            self.rolls.append(Roll(pins))

    def score(self) -> int:
        points = self.total_pins
        if self.is_strike():
            if len(self.next_frame.rolls) == 2:
                points += self.next_frame.total_pins
            else:
                points += self.next_frame.rolls[0].pins + self.next_frame.next_frame.rolls[0].pins
        elif self.is_spare():
            points += self.next_frame.rolls[0].pins

        return points

class TenthFrame(Frame):
    def __init__(self):
        super().__init__()
        self.extra_roll: Optional[Roll] = None

    def add_roll(self, pins: int):
        if len(self.rolls) < 2:
            self.rolls.append(Roll(pins))
        elif len(self.rolls) == 2 and self.extra_roll is None:
            if self.is_strike() or self.is_spare():
                self.extra_roll = Roll(pins)
            else:
                raise IndexError("Can't throw bonus roll with an open tenth frame")
        else:
            raise IndexError("Can't add more than three rolls to the tenth frame")

    def score(self) -> int:
        points = self.total_pins
        if self.is_strike() or self.is_spare():
            return points + self.extra_roll.pins
        return points

class Game:
    MAX_FRAMES: int = 10
    def __init__(self):
        self.frames: list[Frame] = []
        self.__init_frames()
        self.roll_count: int = 0

    def __init_frames(self):
        frame = NormalFrame()
        for i in range(9):
            if i < 8:
                next_frame = NormalFrame()
            else:
                next_frame = TenthFrame()

            frame.next_frame = next_frame
            self.frames.append(frame)
            frame = next_frame

        self.frames.append(frame)

    @property
    def current_frame(self):
        if self.roll_count < (Game.MAX_FRAMES * 2):
            return self.roll_count // 2
        else:
            return Game.MAX_FRAMES - 1

    def roll(self, pins: int):
        self.frames[self.current_frame].add_roll(pins)
        if self.frames[self.current_frame].is_strike():
            self.roll_count += 2
        else:
            self.roll_count += 1

    def score(self) -> int:
        pass