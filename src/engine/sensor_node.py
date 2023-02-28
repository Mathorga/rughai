from engine.node import PositionNode
from engine.shape_node import ShapeNode

class SensorNode(PositionNode):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        anchor_x: int = 0,
        anchor_y: int = 0,
        scaling: int = 1,
        visible: bool = False,
        batch = None,
        group = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.width = width
        self.height = height
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y

        self.__scaling = scaling
        self.__visible = visible

        self.__shape = ShapeNode(
            x = x,
            y = y,
            width = width,
            height = height,
            scaling = scaling,
            anchor_x = anchor_x,
            anchor_y = anchor_y,
            batch = batch,
            group = group
        )

    def set_position(
        self,
        x = None,
        y = None
    ) -> None:
        if x != None:
            self.x = x

        if y != None:
            self.y = y

        self.__shape.set_position(x, y)

    def draw(self) -> None:
        if self.__visible:
            self.__shape.draw()

    def get_bounding_box(self):
        return (
            self.__shape.x - self.anchor_x * self.__scaling,
            self.__shape.y - self.anchor_y * self.__scaling,
            self.width,
            self.height
        )