from enum import Enum

class Colors(Enum):
    """BGR color definitions."""
    RED     = (  0,   0, 255)
    GREEN   = (  0, 255,   0)
    BLUE    = (255,   0,   0)
    YELLOW  = (  0, 255, 255)
    PURPLE  = (128,   0, 128)
    GREY    = (128, 128, 128)
    AMBER   = (  0, 153, 255)

    def __str__(self) -> str:
        return self.name.capitalize()


class Gesture(Enum):
    """Navigation gesture types with associated color and icon."""
    def __new__(cls, value: int, color: Colors):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.color = color
        return obj

    IDLE    = ( 0, Colors.AMBER )
    TRANS   = ( 1, Colors.PURPLE)
    STOP    = ( 2, Colors.RED   )
    ADV     = ( 3, Colors.GREEN )
    RET     = ( 4, Colors.GREEN )
    ACC     = ( 5, Colors.GREEN )
    DEC     = ( 6, Colors.RED   )
    LEFT    = ( 7, Colors.GREEN )
    RIGHT   = ( 8, Colors.GREEN )
    HAIL    = ( 9, Colors.BLUE  )
    ATTN    = (10, Colors.BLUE  )
    POINT   = (11, Colors.BLUE  )
    OTHER   = (12, Colors.GREY  )
    UNLIST  = (13, Colors.GREY  )
    UNCLEAR = (14, Colors.GREY  )

    def __str__(self) -> str:
        return self.name.title()

    @classmethod
    def from_label(cls, label: str) -> "Gesture":
        """Return a Gesture member by case-insensitive name, or None if not found."""
        return cls.__members__.get(label.upper())


# Usage example:
if __name__ == "__main__":
    for gesture in Gesture:
        print(f"{gesture}: value={gesture.value}, color={gesture.color.name}")

