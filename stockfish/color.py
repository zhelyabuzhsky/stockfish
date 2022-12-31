class Color:
    def __init__(self, string: str) -> None:
        self.start = "\x1b["
        self.end = "\x1b[0m"
        self.string = f"{self.start}m{string}{self.end}"
    
    def __str__(self) -> str:
        return self.string
    
    def fg_color(self, color: tuple[int, int, int]):
        red, green, blue = color
        string = self.string[2:-4]
        self.string = f"{self.start};38;2;{red};{green};{blue}{string}{self.end}"
        return self
    
    def bg_color(self, color: tuple[int, int, int]):
        red, green, blue = color
        string = self.string[2:-4]
        self.string = f"{self.start};48;2;{red};{green};{blue}{string}{self.end}"
        return self