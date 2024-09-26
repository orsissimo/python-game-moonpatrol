'''@authors  Simone Orsi (305461) and Martina Gualtieri (308783)'''

from assets import Background, Rover, Hole, Rock, Bullet, Ufo, Cannon
from actor import Actor, Arena
from moonpatrolgame import MoonPatrolGame
import constants

class MoonPatrol(MoonPatrolGame):
    def __init__(self, arena_size: (int, int), configuration_file: str, game_rules_file: str):
        self._w, self._h = arena_size
        self._arena = Arena((self._w, self._h))
        
        self._configuration_file = configuration_file
        self.load_actors(self._configuration_file)
        self._rules, self._keyboard_commands = [], []
        self.read_file_rules(game_rules_file)
        
        self._game_over = False

    def load_actors(self, file: str):    
        with open(file, "r") as f1:
            line = f1.readline()
            
            while line != "":
                if line[len(line)-1] == "\n":
                    line = line[0:len(line)-1]

                split_line = line.split(" ", 1)
                _type = split_line[0] #BACKGROUND, HOLE, ROCK, UFO, CANNON, ROVER  
                
                values = str(split_line[1:][0])
                if values.count(" ") > 0:
                    values = values.split(" ")

                if _type.upper() == constants.BACKGROUND:
                    x, y, speed, setting = values                    
                    self._bg = Background(self._arena, (int(x), int(y)), float(speed), setting)
                elif _type.upper() == constants.HOLE:
                    x, y, explode, size = values
                    self._hole = Hole(self._arena, (int(x), int(y)), bool(explode), size)
                elif _type.upper() == constants.ROCK:
                    x, y, size = values
                    self._rock = Rock(self._arena, (int(x), int(y)), size)
                elif _type.upper() == constants.CANNON:
                    x, y = values
                    self.cannon = Cannon(self._arena, (int(x), int(y)))
                elif _type.upper() == constants.UFO:
                    x, y, speed, vehicle = values
                    self._ufo = Ufo(self._arena, (int(x), int(y)), float(speed), vehicle)
                elif _type.upper() == constants.ROVER:
                    x, y, speed, player = values
                    self._rover = Rover(self._arena, (int(x), int(y)), float(speed), player)
            
                line = f1.readline()

    def read_file_rules(self, file: str):
        lines, keys = [], []
        parse = False
        with open(file, "r") as f1:
            line = f1.readline()
            
            while line != "":
                left_square_brackets = False
                command = ""
            
                if line[len(line)-1] == "\n":
                    line = line[0:len(line)-1]
                if line == constants.FIRST_DELIMITER_RULES:
                    parse = True
                if line != constants.SECOND_DELIMITER_RULES and line != constants.FIRST_DELIMITER_RULES and parse:
                    text = ""
                    if constants.FIRST_DELIMITER_COMMAND in line or constants.SECOND_DELIMITER_COMMAND in line:
                        for string in line:
                            if string == constants.FIRST_DELIMITER_COMMAND:
                                left_square_brackets = True
                            elif left_square_brackets and string != constants.SECOND_DELIMITER_COMMAND:
                                text += string

                            if string == constants.SECOND_DELIMITER_COMMAND:
                                left_square_brackets = False
                                self._keyboard_commands.append(text)
                                text = ""                            

                    lines.append(line)

                if line == constants.SECOND_DELIMITER_RULES:
                    parse = False
                    self._rules.append(lines)
                    lines = []
                    
                line = f1.readline()

        return self._rules

    def commands(self):
        return self._keyboard_commands

    def rules(self, _type: str):
        '''
            _type -> "SINGLE PLAYER", "MULTIPLAYER", "START GAME", "ROVER 1", "ROVER 2", "GAME OVER"
        '''
        return [r for r in self._rules if _type in r][0]

    def actor_type(self, a: Actor) -> str:
        if isinstance(a, Background):
            return constants.BACKGROUND
        elif isinstance(a, Hole):
            return constants.HOLE
        elif isinstance(a, Rock):
            return constants.ROCK
        elif isinstance(a, Cannon):
            return constants.CANNON
        elif isinstance(a, Ufo):
            return constants.UFO
        elif isinstance(a, Rover):
            return constants.ROVER
        elif isinstance(a, Bullet):
            return constants.BULLET

        return ""

    def add_bullet(self, pos: (int, int), direction: str):
        self._bullet = Bullet(self._arena, pos, direction)

    def count_bullets(self) -> int:
        '''Getter for how many bullets of the rover are present in the arena.'''
        count = 0
        for a in self._arena.actors():
            if isinstance(a, Bullet) and a.direction() == constants.BULLET_UP:
                count += 1
        return count

    def remove_second_rover(self) -> bool:
        for a in self._arena.actors():
            if isinstance(a, Rover) and a.player() == constants.PLAYER_2:
                self._arena.remove(a)
                return True
        return False

    def set_speed_background(self):
        for a in self._arena.actors():
            if isinstance(a, Background):
                a.set_speed()
                                    
    def finished(self) -> bool:
        return not (any(isinstance(a, Rover) for a in self._arena.actors())) and not self._game_over

    def restart(self):
        actors = self._arena.actors()
        for a in actors:
            self._arena.remove(a)

        self.load_actors(self._configuration_file)
    
    def arena(self) -> Arena:
        return self._arena
