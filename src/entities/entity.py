from src.management.sprite import LayersEnum
from src.constants import VEC, BLOCK_SIZE

class Entity(Sprite):
    def __init__(self, pos, size, manager: GameManager, layer: int | LayersEnum | None) -> None:
        super().__init__(manager, layer or LayersEnum.ENTITIES)
        self.size = VEC(size)
        self.pos = VEC(pos)
        self.vel = VEC(0, 0)
        self.acc = VEC(0, 0)
        self.rect = pygame.Rect(pos, size)
        self.coords = self.pos // BLOCK_SIZE
    
    def update(self):
        self.vel += self.acc # change later
        self.pos += self.vel * self.manager.dt
    
    def draw(self):
        pass