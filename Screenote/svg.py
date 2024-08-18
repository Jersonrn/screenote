from screeninfo import get_monitors


class SVG:
    def __init__( self, width:int, height:int, name:str, path:str) -> None:
        self.name = name
        self.path = path
        self.width = width
        self.height = height
        self.is_drawing = False
        self.temp_stroke = ""
        self.img = f'''<?xml version="1.0" encoding="UTF-8"?>
    <svg
        version="1.2"
        width="{self.width}px"
        height="{self.height}px"
        xmlns="http://www.w3.org/2000/svg"
        xmlns:ev="http://www.w3.org/2001/xml-events"
        xmlns:xlink="http://www.w3.org/1999/xlink">
        <defs />
    </svg>
    '''
    
    def to_bytes(self):
        return self.img.encode()

    def save(self):
        with open(f"{self.path}/{self.name}.svg", "wb") as file:
            file.write(self.to_bytes())

    def load(self):
        with open(f"./{self.path}/{self.name}.svg", 'r', encoding='utf-8') as file:
            self.img = file.read()

    def add_line(self, x1:int,  y1:int, x2:int, y2:int, color:tuple, stroke_width: int):
        start = self.img[:-15]
        line = f'\t\t<line stroke="rgb{color}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke-width="{stroke_width}px" />\n'
        end = self.img[-15:]

        self.img = start + line + end

    def clean(self):
        self.img = f'''<?xml version="1.0" encoding="UTF-8"?>
    <svg
        version="1.2"
        width="{self.width}px"
        height="{self.height}px"
        xmlns="http://www.w3.org/2000/svg"
        xmlns:ev="http://www.w3.org/2001/xml-events"
        xmlns:xlink="http://www.w3.org/1999/xlink">
        <defs />
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

    img.add_line(100,150,2,2,(255,0,0),10)
    img.save()
