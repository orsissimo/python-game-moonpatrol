'''@authors  Simone Orsi (305461) and Martina Gualtieri (308783)'''

from actor import Arena, Actor

def abstract():
    raise NotImplementedError("Abstract method")

class MoonPatrolGame:
    def load_actors(self, file: str):
        abstract()

    def read_file_rules(self, file: str):
        abstract()

    def commands(self):
        abstract()

    def rules(self, _type: str):
        abstract()

    def actor_type(self, a: Actor) -> str:
        abstract()

    def add_bullet(self, post: (int, int), direction: str) -> bool:
        abstract()

    def count_bullets(self) -> int:
        abstract()

    def remove_second_rover(self) -> bool:
        abstract()

    def set_speed_background(self):
        abstract()

    def finished(self) -> bool:
        abstract()

    def restart(self):
        abstract()
        
    def arena(self) -> Arena:
        abstract()
