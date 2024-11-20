import math
from Screenote.utils import Color
from screeninfo import get_monitors


class Line:
    def __init__(
            self,
            x= 0,
            y= 0,
            fill= Color(None),
            stroke=Color((1,1,1)),
            stroke_width= 4
    ) -> None:
        self.x1 = x
        self.y1 = y
        self.x2: int
        self.y2: int
        self.stroke = stroke
        self.stroke_width = stroke_width

    def get_str(self):
        return f'\t<line stroke="{self.stroke}" x1="{self.x1}" y1="{self.y1}" x2="{self.x2}" y2="{self.y2}" stroke-width="{self.stroke_width}px" />\n'

    def add_point(self, x, y):
        self.x2 = x
        self.y2 = y

class Circle:
    def __init__(
            self,
            x= 0,
            y= 0,
            fill= Color(None),
            stroke=Color((1,1,1)),
            stroke_width= 4
    ) -> None:
        self.cx = x
        self.cy = y
        self.fill = fill
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.radius = 0

    def get_str(self):
        return f'\t<circle r="{self.radius}" cx="{self.cx}" cy="{self.cy}" fill="{self.fill}" stroke="{self.stroke}" stroke-width="{self.stroke_width}" />\n'
    
    def add_point(self, x, y):
        self.radius = math.sqrt( (x - self.cx)**2 + (y - self.cy)**2 )

class Ellipse(Circle):
    def __init__(
            self,
            x=0,
            y=0,
            fill=Color(None),
            stroke=Color((1, 1, 1)),
            stroke_width=4
    ) -> None:
        super().__init__(x, y, fill, stroke, stroke_width)

        self.rx = 0
        self.ry = 0

    def get_str(self):
        return f'\t<ellipse rx="{self.rx}" ry="{self.ry}" cx="{self.cx}" cy="{self.cy}" fill="{self.fill}" stroke="{self.stroke}" stroke-width="{self.stroke_width}" />\n'

    def add_point(self, x, y):
        self.rx = x - self.cx
        self.ry = y - self.cy

class Rectangle:
    def __init__(
            self,
            x=0,
            y=0,
            fill=Color(None),
            stroke=Color((1,1,1)),
            stroke_width=4
    ) -> None:
        self.origin_x = x
        self.origin_y = y
        self.x = x
        self.y = y
        self.width = 0
        self.height = 0
        self.fill = fill
        self.stroke = stroke
        self.stroke_width = stroke_width

    def get_str(self):
        return f'\t<rect x="{self.x}" y="{self.y}" width="{self.width}" height="{self.height}" fill="{self.fill}" stroke="{self.stroke}" stroke_width="{self.stroke_width}" />\n'
    
    def add_point(self, x, y):
        if x > self.origin_x:
            self.width = x - self.x
        else:
            self.x = x
            self.width = self.origin_x - self.x

        if y > self.origin_y:
            self.height = y - self.y
        else:
            self.y = y
            self.height = self.origin_y - self.y

class Polyline:
    def __init__(
            self,
            x=0,
            y=0,
            fill= Color(None),
            stroke= (0., 0., 0.),
            stroke_width= 4
    ) -> None:

        self.points = f"{x},{y} "
        self.fill = fill
        self.stroke = stroke
        self.stroke_width = stroke_width

    def get_str(self):
        return f'\t<polyline points="{self.points}" fill="{self.fill}" stroke="{self.stroke}" stroke-width="{self.stroke_width}" />\n'

    def add_point(self, x, y):
        self.points = self.points + f"{x}, {y} "


class SVG:
    def __init__( self, width:int, height:int, name:str, path:str) -> None:
        self.name = name
        self.path = path

        self.width = width
        self.height = height

        self.stroke = None
        self.strokes = []
        self.undo_strokes = []

        self.img = f'''<?xml version="1.0" encoding="UTF-8"?>
    <svg
        height="{self.height}px"
        width="{self.width}px"
        xmlns="http://www.w3.org/2000/svg">
    </svg>
'''

    def create_stroke(self, stroke_type: str, **kwargs):
        stroke_classes = {
            "polyline": Polyline,
            "circle": Circle,
            "ellipse": Ellipse,
            "rectangle": Rectangle,
            "line": Line,
        }

        stroke_type = stroke_type.lower()

        if stroke_type not in stroke_classes:
            raise ValueError("Unknown type, use: 'polyline', 'circle', 'ellipse', 'rectangle' or 'line'")

        required_args = ["x", "y", "fill", "stroke", "stroke_width"]

        missing_args = [arg for arg in required_args if arg not in kwargs]
        if missing_args:
            raise ValueError(f"Missing arguments: {', '.join(missing_args)}")

        self.stroke = stroke_classes[stroke_type](
                x=kwargs["x"],
                y=kwargs["y"],
                fill=kwargs["fill"],
                stroke=kwargs["stroke"],
                stroke_width=kwargs["stroke_width"]
        )

    def add_point(self, x, y):
        if self.stroke != None:
            self.stroke.add_point(x, y)

    def add_stroke(self):
        if self.undo_strokes:
            self.undo_strokes.clear()

        if self.stroke is not None:
            self.strokes.append(self.stroke)
            self.stroke = None

    def remove_last_stroke(self):
        if self.strokes:
            last_stroke = self.strokes.pop()
            self.undo_strokes.append(last_stroke)

    def recove_next_stroke(self):
        if self.undo_strokes:
            next_stroke = self.undo_strokes.pop()
            self.strokes.append(next_stroke)

    def get_image(self):
        image = self.img[:-7]
        end = self.img[-7:]

        for stroke in self.strokes:
            image += stroke.get_str()

        if self.stroke is not None:
            image += self.stroke.get_str()

        return image + end


    def to_bytes(self):
        return self.get_image().encode()

    def save(self):
        with open(f"{self.path}/{self.name}.svg", "wb") as file:
            file.write(self.to_bytes())

    def load(self):
        with open(f"./{self.path}/{self.name}.svg", 'r', encoding='utf-8') as file:
            self.img = file.read()

    def add_line(self, x1:int,  y1:int, x2:int, y2:int, color:tuple, stroke_width: int):
        start = self.img[:-7]
        line = f'\t\t<line stroke="rgb{color}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke-width="{stroke_width}px" />\n'
        end = self.img[-7:]

        self.img = start + line + end

    def clean(self):
        self.img = f'''<?xml version="1.0" encoding="UTF-8"?>
    <svg
        height="{self.height}px"
        width="{self.width}px"
        xmlns="http://www.w3.org/2000/svg">
    </svg>
'''

if __name__ == "__main__":
    monitors = get_monitors()
    img = SVG(
            width=monitors[0].width,
            height=monitors[0].height,
            name="hello",
            path="./images"
    )

    # img.add_line(100,150,2,2,(255,0,0),10)
    img.create_stroke(
            "polyline",
            points=f"0,0 ",
            fill="none",
            stroke=(0,0,255),
            stroke_width=10
            )
    img.add_point(50, 50)
    img.add_point(70, 100)
    img.add_stroke()
    img.save()
