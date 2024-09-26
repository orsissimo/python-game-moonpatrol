'''@authors  Simone Orsi (305461) and Martina Gualtieri (308783)'''

import random, math, constants
from actor import Actor, Arena

# -- Background -----
class Background(Actor):
    def __init__(self, arena, pos, s, setting):
        self._x, self._y = pos
        self._dx = -s
        self._setting = setting

        self._arena = arena
        arena.add(self)

        self._img_x, self._img_y, self._w, self._h = self.symbol()

    def collide(self, other):
        if self._setting == constants.GROUND and isinstance(other, Bullet) and other.direction() == constants.BULLET_DOWN:
            if random.randint(0, 4) == 0:
                hole = Hole(self._arena, (other.position()[0], self._y), True, constants.SMALL_SIZE)
            self._arena.remove(other)
            return True
        return False
    
    def move(self):
        self._x += self._dx
        if self._x + self._dx < -constants.MAX_IMAGE_WIDTH:
            self._x = constants.MAX_IMAGE_WIDTH
            self._x += self._dx

    def position(self):
        return self._x, self._y, self._w, self._h

    def arena(self):
        arena_w, arena_h = self._arena.size()
        return arena_w, arena_h

    def symbol(self):
        if self._setting == constants.MOUNTAINS:
            return 0, 50, 512, 210
        elif self._setting == constants.HILLS:
            return 0, 256, 512, 126
        elif self._setting == constants.CITY:
            return 0, 384, 512, 70
        elif self._setting == constants.GROUND:
            return 0, 512, 512, 15 

    def setting(self):
        return self._setting

    def get_speed(self):
        return self._dx

    def set_speed(self):
        self._dx -= 1

    def priority(self):
        return constants.LOW_PRIORITY

class Obstacle(Actor):
    def collide(self, other):
        raise NotImplementedError('Abstract method')

    def move(self):
        self._dx = self.speed()
        arena_w, arena_h = self._arena.size()
        self._x += self._dx
        if self._x + self._w < 0:
            self._x = random.randint(arena_w, arena_w*2)
            '''   x is a random number between canvas width and 4 times this size.
            This way there is more space to move objects.
            '''
            self.check_position()

    def reset_x(self):
        self._x = constants.NEGATIVE_X
        self.move()

    def check_position(self):
        arena_w, arena_h = self._arena.size()

        move_element = True
        while move_element:
           move_element = False
           for a in self._arena.actors():
                if self is not a and isinstance(a, Obstacle):
                    a_x, a_y, a_w, a_h = a.position()
                    distance_0 = self._x - (a_x + a_w)
                    distance_1 = a_x - (self._x + self._w)
                    
                    #Check whether the objects are sufficiently spaced
                    if abs(distance_0) <= constants.MIN_DISTANCE or abs(distance_1) <= constants.MIN_DISTANCE:
                        self._x = random.randint(arena_w, arena_w*4)
                        move_element = True

    def position(self) -> (int, int, int, int):
        return self._x, self._y, self._w, self._h

    def symbol(self) -> (int, int, int, int):
        raise NotImplementedError('Abstract method')

    def speed(self):
        ground = None
        for a in self._arena.actors():
            if isinstance(a, Background) and a.setting() == constants.GROUND:
                ground = a
                
        if ground != None:
            return int(ground.get_speed())
        else:
            return constants.OBSTACLE_SPEED

    def priority(self) -> int:
        return constants.MEDIUM_LOW_PRIORITY

# -- Hole -----
class Hole(Obstacle):
    def __init__(self, arena, pos, explode, size):
        self._x, self._y = pos
        self._explode = explode
        self._size = size

        self._arena = arena
        arena.add(self)
        
        self._img_x, self._img_y, self._w, self._h = self.symbol()
        self._dx = self.speed()
        self.check_position()

    def collide(self, other):
        pass

    def move(self):
        self._dx = self.speed()
        
        arena_w, arena_h = self._arena.size()
        self._x += self._dx
        if self._x + self._w < 0:
            if not self._explode:
                self._x = random.randint(arena_w, arena_w*2)
                '''   x is a random number between canvas width and 4 times this size.
                This way there is more space to move objects.
                '''
                self.check_position()
            else:
                self._arena.remove(self)

    def symbol(self):
        if self._size == constants.SMALL_SIZE:
            return 138, 140, 13, 12
        elif self._size == constants.BIG_SIZE:
            return 154, 140, 25, 13    

# -- Rock -----
class Rock(Obstacle):
    def __init__(self, arena, pos, size):
        self._x, self._y = pos
        self._size = size
        self._damaged = False

        self._arena = arena
        arena.add(self)

        self._img_x, self._img_y, self._w, self._h = self.symbol()
        
    def collide(self, other):
        if isinstance(other, Rover) or (isinstance(other, Bullet) and self._size == constants.SMALL_SIZE):
            self.reset_x()
            return True
        elif isinstance(other, Bullet) and self._size == constants.BIG_SIZE:
            if self._damaged:
                self.reset_x()                
                self._damaged = False
                return True
            else:
                self._damaged = True
                
        return False

    def symbol(self):
        if self._size == constants.SMALL_SIZE:
            return 80, 203, 14, 12
        elif self._size == constants.BIG_SIZE:
            return 112, 199, 13, 16

# -- Cannon -----
class Cannon(Obstacle):
    def __init__(self, arena, pos):
        self._x, self._y = pos

        self._arena = arena
        arena.add(self)

        self._img_x, self._img_y, self._w, self._h = self.symbol()

    def collide(self, other):
        if (isinstance(other, Rover) or
        (isinstance(other, Bullet) and (other.direction() == constants.BULLET_UP or other.direction() == constants.BULLET_RIGHT))):
            self.reset_x()
            return True
        return False

    def symbol(self):
        return 109, 246, 16, 16
    
# -- Bullet -----
class Bullet(Actor):
    def __init__(self, arena, pos, direction):
        self._initial_x, self._initial_y = pos
        self._x, self._y = self._initial_x, self._initial_y
        self._img_x, self._img_y, self._w, self._h = 0, 0, 0, 0
        self._direction = direction
        self._distance = 120
        self._dy, self._dx = 6, 0
        
        self._arena = arena
        arena.add(self)
        
        self._img_x, self._img_y, self._w, self._h = self.symbol()

    def collide(self, other):
        if isinstance(other, Rock) or (isinstance(other, Bullet) and other.direction() != self._direction):
            self._arena.remove(self)
            return True
        return False

    def move(self):
        self._dx = self.speed()
        
        arena_w, arena_h = self._arena.size()
        if self._direction == constants.BULLET_UP:
            self._y -= self._dy
            if self._y < 0:
                self._arena.remove(self)
                
        elif self._direction == constants.BULLET_RIGHT:
            self._x += self._dx
            if self._x > self._initial_x + self._distance:
                self._arena.remove(self)

        elif self._direction == constants.BULLET_DOWN:
            self._y += self._dy
            if self._x < 0 or self._x > arena_w:
                self._arena.remove(self)

        elif self._direction == constants.BULLET_LEFT:
            self._x -= self._dx
            if self._x < 0 or self._x > arena_w:
                self._arena.remove(self)

    def position(self):
        return self._x, self._y, self._w, self._h

    def symbol(self):
        if self._direction == constants.BULLET_UP:
            self._img_x, self._img_y, self._w, self._h = 197, 231, 5, 5
            
        elif self._direction == constants.BULLET_RIGHT:
            if self._initial_x < self._x < self._initial_x + self._distance/2:
                self._img_x, self._img_y, self._w, self._h = 193, 143, 10, 4
                
            elif self._initial_x + self._distance/2 < self._x < self._initial_x + 3 * self._distance/4:
                self._img_x, self._img_y, self._w, self._h = 225, 142, 6, 7
                
            elif self._initial_x + 3 * self._distance/4 < self._x < self._initial_x + self._distance:
                self._img_x, self._img_y, self._w, self._h = 239, 140, 8, 10
                
        elif self._direction == constants.BULLET_LEFT:
            self._img_x, self._img_y, self._w, self._h = 215, 143, 4, 4
            
        elif self._direction == constants.BULLET_DOWN:
            self._img_x, self._img_y, self._w, self._h = 213, 231, 5, 6

        return self._img_x, self._img_y, self._w, self._h
                
    def direction(self):
        return self._direction

    def priority(self):
        return constants.MEDIUM_HIGH_PRIORITY

    def speed(self):
        ground = None
        for a in self._arena.actors():
            if isinstance(a, Background) and a.setting() == constants.GROUND:
                ground = a
                
        if ground != None:
            speed = -int(ground.get_speed())
            if self._direction == constants.BULLET_LEFT:
                speed *= 2
            return speed
        else:
            if self._direction == constants.BULLET_LEFT:
                return constants.BULLET_LEFT_SPEED
            else:
                return constants.BULLET_SPEED

# -- Ufo -----
class Ufo(Actor):
    def __init__(self, arena, pos, s, vehicle):
        self._x, self._y = pos
        self._y_backup = self._y
        self._count, self._timer = 0, 0
        self._img_x, self._img_y, self._w, self._h = 0, 0, 0, 0
        self._left, self._up = True, False
        self._rotate = False
        self._vehicle = vehicle

        self._dx = -s
        if self._vehicle == constants.SHOOTER_UFO:
            self._dy = -(s/3)
        elif self._vehicle == constants.BONUS_UFO:
            self._dy = -(s/2)

        self._arena = arena
        arena.add(self)

        self._img_x, self._img_y, self._w, self._h = self.symbol()

    def collide(self, other):
        if isinstance(other, Bullet) and other.direction() != constants.BULLET_DOWN:
            arena_w, arena_h = self._arena.size()
            if self._vehicle == constants.BONUS_UFO:
                for r in self._arena.actors():
                    if isinstance(r, Rover):
                        r.set_invincible()
                        self._timer = 1
                        
            self._x = arena_w + 300
            self._left = True
            return True
        return False

    def move(self):
        if self._x % 30 == 0:
            self._rotate = not self._rotate
            
        arena_w, arena_h = self._arena.size()
        if self._x + self._dx < constants.MARGIN:
            self._left = False
        elif self._x + self._dx > arena_w - constants.MARGIN:
            self._left = True

        if self._left:
            self._x += self._dx
        else:
            self._x -= self._dx

        if self._vehicle == constants.SHOOTER_UFO:
            random_dy = random.choice([self._dy, -self._dy])
            if self._y + random_dy < constants.MARGIN or self._y + random_dy > constants.TOP_MARGIN_SHOOTER_UFO:
                self._y -= random_dy
            else:
                self._y += random_dy

        elif self._vehicle == constants.BONUS_UFO:
            if self._y + self._dy < constants.MARGIN:
                self._up = False
            elif self._y + self._dy > constants.TOP_MARGIN_BONUS_UFO:
                self._up = True

            if self._up:
                self._y += self._dy
            else:
                self._y -= self._dy          

        if self._timer > 0:
            self._timer += 1
            
        if self._timer == constants.MAX_TIMER:
            for r in self._arena.actors():
                if isinstance(r, Rover):
                    r.set_invincible()
                    self._timer = 0

    def get_rotate(self):
        return self._rotate

    def position(self):
        return self._x, self._y, self._w, self._h

    def arena(self):
        arena_w, arena_h = self._arena.size()
        return arena_w, arena_h

    def symbol(self):
        if self._vehicle == constants.SHOOTER_UFO:
            self._img_x, self._img_y, self._w, self._h = 67, 230, 15, 8
        elif self._vehicle == constants.BONUS_UFO:
            if self._rotate:
                self._img_x, self._img_y, self._w, self._h = 104, 226, 13, 16
            else:
                self._img_x, self._img_y, self._w, self._h = 88, 227, 14, 14

        return self._img_x, self._img_y, self._w, self._h

    def priority(self):
        return constants.MEDIUM_LOW_PRIORITY

# -- Rover -----
class Rover(Actor):
    def __init__(self, arena, pos, s, player):
        self._x, self._y = pos
        self._dx, self._dy, self._g, self._speed = 0, 0, 0.4, s
        self._damaged, self._firstrun, self._invincible = False, True, False
        self._img_x, self._img_y, self._w, self._h = 0, 0, 0, 0
        self._destruction_timer = 0
        self._player = player
        self._sprite_type = ""

        self._arena = arena
        arena.add(self)

        self._img_x, self._img_y, self._w, self._h = self.symbol()

    def move(self):
        arena_w, arena_h = self._arena.size()
        if not self._damaged:
            self._y += self._dy
            self._dy += self._g

            if (self._y > constants.GROUND_LEVEL - self._h):
                self._y = constants.GROUND_LEVEL - self._h
                self._dy = 0

            self._x += self._dx
            if self._x < 0:
                self._x = 0
            elif self._x > arena_w - self._w:
                self._x = arena_w - self._w

        elif self._damaged:
            self._destruction_timer += 1
            
        if self._damaged and self._destruction_timer > 30:
            self._arena.remove(self)

    def go_right(self):
        self._dx, self._dy = +self._speed, 0

    def go_left(self):
        self._dx, self._dy = -self._speed * 2, 0

    def stay(self):
        self._dx, self._dy = 0, 0

    def jump(self):
        arena_w, arena_h = self._arena.size() #Arena size getter
        if self._y >= constants.GROUND_LEVEL - self._h:
            self._dy = -6

    def set_invincible(self):
        self._invincible = not self._invincible

    def damaged(self):
        return self._damaged

    def collide(self, other):
        if not self._invincible: #Just for testing purposes, I swear I never cheated.. almost never
            if (isinstance(other, Hole) or isinstance(other, Rock) or isinstance(other, Cannon) or 
            (isinstance(other, Bullet) and (other.direction() == constants.BULLET_DOWN or other.direction() == constants.BULLET_LEFT))):
                self._damaged = True
                return True
        return False

    def position(self):
        return self._x, self._y, self._w, self._h

    def player(self):
        return self._player

    def arena(self):
        arena_w, arena_h = self._arena.size()
        return arena_w, arena_h

    def get_sprite_type(self):
        return self._sprite_type

    def symbol(self):
        ''' #(I) As long as rover is invincible
        '''
        ''' #(A) As long as rover is alive and not invincible
        '''
        ''' #(D) As long as rover is beeing destroyed
        '''

        if self._player == constants.PLAYER_1:
            if self._invincible:    # -- P1(I) ----
                if self._destruction_timer <= 0:
                    if self._dy < 0:
                        self._sprite_type = constants.JUMPING_SPRITE
                        self._img_x, self._img_y, self._w, self._h = 8, 285, 27, 26     #Jumping sprite
                    else:
                        self._sprite_type = constants.DEFAULT_SPRITE
                        self._img_x, self._img_y, self._w, self._h = 6, 250, 32, 23     #Default sprite

            else:                   # -- P1(A) -----
                if self._destruction_timer <= 0:
                    if self._dy < 0:
                        self._sprite_type = constants.JUMPING_SPRITE
                        self._img_x, self._img_y, self._w, self._h = 47, 103, 27, 27    #Jumping sprite
                    else:
                        self._sprite_type = constants.DEFAULT_SPRITE
                        self._img_x, self._img_y, self._w, self._h = 212, 158, 32, 23   #Default sprite

                                    # -- P1(D) ----
                if 0 < self._destruction_timer < constants.ROVER_DESTRUCTION_ANIMATION_0:
                    if self._destruction_timer == 4:
                        self._y -= 4
                    self._img_x, self._img_y, self._w, self._h = 113, 101, 46, 32
                elif constants.ROVER_DESTRUCTION_ANIMATION_0 < self._destruction_timer < constants.ROVER_DESTRUCTION_ANIMATION_1:
                    self._img_x, self._img_y, self._w, self._h = 165, 101, 42, 32
                elif constants.ROVER_DESTRUCTION_ANIMATION_1 < self._destruction_timer < constants.ROVER_DESTRUCTION_ANIMATION_2:
                    if self._destruction_timer == 4:
                        self._y += 1
                    self._img_x, self._img_y, self._w, self._h = 214, 102, 41, 30

        elif self._player == constants.PLAYER_2:
            if self._invincible:    # -- P2(I) ----
                if self._destruction_timer <= 0:
                    if self._dy < 0:
                        self._sprite_type = constants.JUMPING_SPRITE
                        self._img_x, self._img_y, self._w, self._h = 50, 284, 27, 27    #Jumping sprite
                    else:
                        self._sprite_type = constants.DEFAULT_SPRITE
                        self._img_x, self._img_y, self._w, self._h = 47, 250, 32, 23    #Default sprite

            else:                   # -- P2(A) -----
                if self._destruction_timer <= 0:
                    if self._dy < 0:
                        self._sprite_type = constants.JUMPING_SPRITE
                        self._img_x, self._img_y, self._w, self._h = 49, 152, 27, 27    #Jumping sprite
                    else:
                        self._sprite_type = constants.DEFAULT_SPRITE
                        self._img_x, self._img_y, self._w, self._h = 248, 158, 32, 23   #Default sprite

                                    # -- P2(D) ----
                if 0 < self._destruction_timer < constants.ROVER_DESTRUCTION_ANIMATION_0:
                    if self._destruction_timer == 4:
                        self._y -= 4
                    self._img_x, self._img_y, self._w, self._h = 113, 101, 46, 32
                elif constants.ROVER_DESTRUCTION_ANIMATION_0 < self._destruction_timer < constants.ROVER_DESTRUCTION_ANIMATION_1:
                    self._img_x, self._img_y, self._w, self._h = 165, 101, 42, 32
                elif constants.ROVER_DESTRUCTION_ANIMATION_1 < self._destruction_timer < constants.ROVER_DESTRUCTION_ANIMATION_2:
                    if self._destruction_timer == 4:
                        self._y += 1
                    self._img_x, self._img_y, self._w, self._h = 214, 102, 41, 30
                
        return self._img_x, self._img_y, self._w, self._h

    def priority(self):
        return constants.HIGH_PRIORITY
