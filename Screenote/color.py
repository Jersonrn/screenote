class Color:
    def __init__(self, color):
        if color is None or str(color).lower() == "none":
            self.color = "none"
        elif isinstance(color, tuple) and len(color) == 3:
            self.color = f"rgb({color[0]},{color[1]},{color[2]})"
        else:
            raise ValueError("Invalid color format. Use None, 'None', 'none', or an RGB tuple.")

    def __str__(self):
        return self.color


if __name__ == "__main__":
    print(Color(None))
    print(Color("None"))
    print(Color("none"))
    print(Color((255, 0, 0)))

    color = Color((0,255,0))
    print(f"color: {color}")
