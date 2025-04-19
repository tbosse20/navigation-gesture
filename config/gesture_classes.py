from enum import Enum

class Colors(Enum):
    """RGB color definitions."""
    RED     = (255, 0, 0)
    GREEN   = (0, 255, 0)
    BLUE    = (0, 0, 255)
    YELLOW  = (255, 255, 0)
    PURPLE  = (128, 0, 128)
    GREY    = (128, 128, 128)
    AMBER   = (255, 153, 0)

    def __str__(self) -> str:
        return self.name.capitalize()


class Gesture(Enum):
    """Navigation gesture types with associated color and icon."""
    def __new__(cls, value: int, color: Colors, icon: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.color = color
        obj.icon = icon
        return obj

    IDLE    = (0,  Colors.AMBER  )
    TRANS   = (1,  Colors.PURPLE )
    STOP    = (2,  Colors.RED    )
    ADV     = (3,  Colors.GREEN  )
    ACC     = (4,  Colors.GREEN  )
    DEC     = (5,  Colors.RED    )
    REV     = (6,  Colors.GREEN  )
    UTURN   = (7,  Colors.GREEN  )
    PASS    = (8,  Colors.GREEN  )
    LEFT    = (9,  Colors.GREEN  )
    RIGHT   = (10, Colors.GREEN  )
    HAIL    = (11, Colors.BLUE   )
    POINT   = (12, Colors.BLUE   )
    OTHER   = (13, Colors.GREY   )

    def __str__(self) -> str:
        return self.name.title()

    @classmethod
    def from_label(cls, label: str) -> "Gesture":
        """Return a Gesture member by case-insensitive name, or None if not found."""
        return cls.__members__.get(label.upper())


# Usage example:
if __name__ == "__main__":
    for gesture in Gesture:
        print(f"{gesture}: value={gesture.value}, color={gesture.color.name}, icon={gesture.icon}")

