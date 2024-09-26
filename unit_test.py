'''@authors  Simone Orsi (305461) and Martina Gualtieri (308783)'''

import unittest, constants
from assets import Background, Rover, Hole, Rock, Bullet, Ufo, Cannon
from actor import Arena

class BackgroundTest(unittest.TestCase):

    def setUp(self):
        self._arena = Arena((constants.ARENA_WIDTH, constants.ARENA_HEIGHT))
        self._background_values = (((50, 0), 1, constants.MOUNTAINS),
                                   ((470, 150), 2, constants.HILLS),
                                   ((50, 247), 4, constants.GROUND),
                                   ((150, 150), 2, constants.CITY))

    def test_symbol(self):
        for param in self._background_values:
            pos, speed, player = param
            with self.subTest(param=param):
                background = Background(self._arena, pos, speed, player)
                background.move()                

                if background.setting() == constants.MOUNTAINS:
                    self.assertTrue(background.symbol() == (0, 50, 512, 210))
                elif background.setting() == constants.HILLS:
                    self.assertTrue(background.symbol() == (0, 256, 512, 126))
                elif background.setting() == constants.CITY:
                    self.assertTrue(background.symbol() == (0, 384, 512, 70))
                elif background.setting() == constants.GROUND:
                    self.assertTrue(background.symbol() == (0, 512, 512, 15 ))

    def test_collision(self):        
        bullet = Bullet(self._arena, (50, 245), constants.BULLET_DOWN)
        
        for param in self._background_values:
            pos, speed, player = param
            with self.subTest(param=param):
                background = Background(self._arena, pos, speed, player)
                background.move()
                                
                if background.setting() == constants.GROUND:
                    self.assertTrue(self._arena.check_collision(background, bullet))
                    
                
class RoverTest(unittest.TestCase):

    def setUp(self):
        self._arena = Arena((constants.ARENA_WIDTH, constants.ARENA_HEIGHT))
        self._rover_values = (((40, 250), 2.3, constants.PLAYER_2),
                              ((60, 230), 2.3, constants.PLAYER_1),
                              ((50, 200), 2.3, constants.PLAYER_1),
                              ((100, 247), 2.3, constants.PLAYER_1))

    def test_jump(self):
        for param in self._rover_values:
            pos, speed, player = param
            with self.subTest(param=param):
                rover = Rover(self._arena, pos, speed, player)
            
                rover.jump()
                rover.move()

                new_pos = rover.position()[0], rover.position()[1]
                self.assertTrue(new_pos[1] <= pos[1])

    def test_symbol(self):        
        for param in self._rover_values:
            pos, speed, player = param
            with self.subTest(param=param):
                rover = Rover(self._arena, pos, speed, player)
            
                rover.move()
                rover.jump()
                
                new_pos = rover.position()[0], rover.position()[1]

                if new_pos[1] <= pos[1] and new_pos[1] != pos[1]:
                    if rover.player() == constants.PLAYER_1:
                        self.assertTrue(rover.symbol() == (47, 103, 27, 27))
                    else:
                        self.assertTrue(rover.symbol() == (49, 152, 27, 27))
                else:
                    if rover.player() == constants.PLAYER_1:
                        self.assertTrue(rover.symbol() == (212, 158, 32, 23))
                    else:
                        self.assertTrue(rover.symbol() == (248, 158, 32, 23))
                        

class HoleTest(unittest.TestCase):

    def setUp(self):
        self._arena = Arena((constants.ARENA_WIDTH, constants.ARENA_HEIGHT))
        self._hole = Hole(self._arena, (60, 247), False, constants.SMALL_SIZE)

    def test_collision(self):
        rover = Rover(self._arena, (65, 247), 2.3, constants.PLAYER_1)        

        self._hole.move()
        self.assertTrue(self._arena.check_collision(self._hole, rover))
        

class RockTest(unittest.TestCase):

    def setUp(self):
        self._arena = Arena((constants.ARENA_WIDTH, constants.ARENA_HEIGHT))
        self._rock = Rock(self._arena, (150, 236), constants.BIG_SIZE)

    def test_collision(self):
        bullet = Bullet(self._arena, (152, 247), constants.BULLET_RIGHT)

        self._rock.move()
        self.assertTrue(self._arena.check_collision(self._rock, bullet))

    def test_position(self):
        cannon = Cannon(self._arena, (200, 247))
        cannon_pos = cannon.position()[0], cannon.position()[1]
        
        self._rock.check_position()
        rock_pos = self._rock.position()[0], self._rock.position()[1]
        
        self.assertTrue(rock_pos[0] + constants.MIN_DISTANCE > cannon_pos[0])
        

class UfoTest(unittest.TestCase):

    def setUp(self):
        self._arena = Arena((constants.ARENA_WIDTH, constants.ARENA_HEIGHT))
        self._ufo = Ufo(self._arena, (100, 50), 4, constants.BONUS_UFO)

    def test_collision(self):
        bullet = Bullet(self._arena, (105, 55), constants.BULLET_UP)

        self._ufo.move()
        self.assertTrue(self._arena.check_collision(self._ufo, bullet))

    def test_symbol(self):
        self._ufo.move()

        if self._ufo.get_rotate():
            self.assertTrue(self._ufo.symbol() == (104, 226, 13, 16))
        else:
            self.assertTrue(self._ufo.symbol() == (88, 227, 14, 14))
                    
if __name__ == '__main__':
    unittest.main()
