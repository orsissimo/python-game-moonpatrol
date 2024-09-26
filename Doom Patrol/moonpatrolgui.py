'''@authors  Simone Orsi (305461) and Martina Gualtieri (308783)'''

import g2d_pyg as g2d
import datetime, random
from assets import Background
from moonpatrolgame import MoonPatrolGame
import constants

class MoonPatrolGui:
    def __init__(self, g: MoonPatrolGame):
        self._game = g
        
        self._arena = self._game.arena()
        self._arena_width, self._arena_height = self._arena.size()
        self._sprite, self._background_image = g2d.load_image(constants.FOREGROUND_IMAGE), g2d.load_image(constants.BACKGROUND_IMAGE)
        self._background_music, self._game_over_music = g2d.load_audio(constants.BACKGROUND_MUSIC), g2d.load_audio(constants.GAME_OVER_MUSIC)
        self._game_over_sound_played, self._background_sound_played = False, False
        
        self._start_game, self._time, self._elapsed_time = False, True, False
        self._start_time, self._end_time = 0, (0, 0, 0)
        self._count_player = 0
        self._rover = None

        self._score, self._level = 0, 1

        '''self._game.commands() return ['1', '2', 'Enter', 'Backspace', 'w', 'a', 's', 'd', 'e', 'i', 'j', 'k', 'l', 'o', 'Spacebar']'''
        (self._key_1, self._key_2, self._key_start_game, self._key_go_back, self._key_up_1, self._key_left_1, self._key_stay_1, self._key_right_1, self._key_bullet_1,
         self._key_up_2, self._key_left_2, self._key_stay_2, self._key_right_2, self._key_bullet_2, self._key_restart) = 'Digit1', 'Digit2', 'Enter', 'Backspace', 'KeyW', 'KeyA', 'KeyS', 'KeyD', 'KeyE', 'KeyI', 'KeyJ', 'KeyK', 'KeyL', 'KeyO', 'Spacebar'

    def tick(self):
        self.handle_keyboard()
        
        if not self._start_game:
            self.rules()
        else:
            if self._count_player == 1:
                self._game.remove_second_rover()
                
            if self._time:
                self._start_time = datetime.datetime.now()
                self._time = False

            if self._score > 0 and self._score % constants.STEP_LEVEL == 0 and self._level <= constants.LEVEL_NUMBERS:
                self._level += 1
                self._game.set_speed_background()

            self._arena.move_all()
            g2d.clear_canvas()

            actors = sorted(self._arena.actors(), key=lambda obj: obj.priority(), reverse=True)
            for a in actors:
                if self._game.actor_type(a) == constants.BACKGROUND:
                    image = self._background_image
                else:
                    image = self._sprite
                    
                g2d.draw_image_clip(image, a.symbol(), a.position())

                if self._game.actor_type(a) == constants.CANNON and random.randint(0, 40) == 30:
                    cannon_x, cannon_y, cannon_w, cannon_h = a.position()
                    if 0 <= cannon_x <= self._arena_width:
                        self._game.add_bullet((cannon_x - 4, cannon_y + 1), constants.BULLET_LEFT) #-4 and +1 cause the bullets to be generated from the "mouth" of the cannon

                if self._game.actor_type(a) == constants.UFO and random.randint(0, 120) == 30:
                    ufo_x, ufo_y, ufo_w, ufo_h = a.position()
                    if 0 <= ufo_x <= self._arena_width:
                        self._game.add_bullet((ufo_x, ufo_y), constants.BULLET_DOWN)
                        
            if not self._game.finished():
                self._score += 1
            else:
                if not self._elapsed_time:
                    self._end_time = self.get_time(datetime.datetime.now() - self._start_time)
                    self._elapsed_time = True

                self.game_over()

            self.score()
            self.soundtrack()
                
    def soundtrack(self):
        if not self._game.finished():
            if not self._background_sound_played:
                g2d.pause_audio(self._game_over_music)
                g2d.play_audio(self._background_music, True)
                self._background_sound_played = True
        else:
            if not self._game_over_sound_played:
                g2d.pause_audio(self._background_music)
                g2d.play_audio(self._game_over_music, False)
                self._game_over_sound_played = True

    def handle_keyboard(self):
        if not self._start_game:
            if self._count_player == 0:
                if g2d.key_pressed(self._key_1):
                    self._count_player = 1
                    
                elif g2d.key_pressed(self._key_2):
                    self._count_player = 2
                    
            elif self._count_player > 0:
                if g2d.key_pressed(self._key_start_game):
                    g2d.pause_audio(self._game_over_music)
                    self._start_game = True
                
            if g2d.key_pressed(self._key_go_back):
                self._count_player = 0
                self.rules()
        else:
            if g2d.key_pressed(self._key_restart) and self._game.finished():
                self.restart_game()
            else:
                for a in self._arena.actors():
                    if self._game.actor_type(a) == constants.ROVER:
                        if a.player() == constants.PLAYER_1:
                            up, left, stay, right, bullet = self._key_up_1, self._key_left_1, self._key_stay_1, self._key_right_1, self._key_bullet_1
                            invincible = constants.KEY_INVINCIBLE_ROVER_1
                        elif a.player() == constants.PLAYER_2:
                            up, left, stay, right, bullet = self._key_up_2, self._key_left_2, self._key_stay_2, self._key_right_2, self._key_bullet_2
                            invincible = constants.KEY_INVINCIBLE_ROVER_2

                        if g2d.key_pressed(up):
                            a.jump()
                        elif g2d.key_pressed(right):
                            a.go_right()
                        elif g2d.key_pressed(left):
                            a.go_left()
                        elif (g2d.key_released(right) or g2d.key_released(left) or
                            g2d.key_released(left) or g2d.key_pressed(stay) or g2d.key_pressed(stay)):
                            a.stay()
                            
                        if g2d.key_pressed(invincible):
                            a.set_invincible() #Just for testing purposes, I swear I never cheated.. almost never

                        if g2d.key_pressed(bullet) and self._game.count_bullets() < constants.MAX_BULLETS and not a.damaged():
                            rover_x, rover_y, rover_w, rover_h = a.position()

                            if a.get_sprite_type() == constants.DEFAULT_SPRITE:
                                bullet_up_x, bullet_up_y = rover_x + 8, rover_y - 2 #+8 and -2 cause the bullets to be generated from the cannon of the rover
                                bullet_right_x, bullet_right_y = rover_x + 34, rover_y + 8 #+34 and +8 cause the bullets to be generated from the cannon of the rover
                            elif a.get_sprite_type() == constants.JUMPING_SPRITE:
                                bullet_up_x, bullet_up_y = rover_x, rover_y + 2 #+2 cause the bullets to be generated from the cannon of the rover while jumping
                                bullet_right_x, bullet_right_y = rover_x + 20, rover_y #+20 cause the bullets to be generated from the cannon of the rover while jumping
                                    
                            self._game.add_bullet((bullet_up_x, bullet_up_y), constants.BULLET_UP)
                            self._game.add_bullet((bullet_right_x, bullet_right_y), constants.BULLET_RIGHT)

    def score(self):
        g2d.set_color(constants.WHITE)
        g2d.draw_image_clip(self._sprite, (160, 13, 89, 14), (10, 10, 60, 9)) #Score
        g2d.draw_text(str(self._score), (75, 9), constants.MEDIUM_FONT_SIZE)
        g2d.draw_image_clip(self._sprite, (161, 36, 89, 14), (self._arena_width - 100, 10, 60, 9)) #Level
        g2d.draw_text(str(self._level), (self._arena_width - 35, 9), constants.MEDIUM_FONT_SIZE)

    def restart_game(self) -> bool:
        self._game.restart()
        gui_play(self._game)

    def game_over(self) -> bool:
        g2d.set_color(constants.BLACK)
        g2d.fill_rect((0, 95, self._arena_width, 65))

        g2d.set_color(constants.WHITE)
        g2d.draw_image_clip(self._sprite, (161, 59, 133, 14), (179, 105, 133, 14)) #Game over
        self.draw_text_rules(self._game.rules(constants.GAME_OVER)[1:], 0, self._arena_width // 2, 133, constants.BIG_FONT_SIZE)
        g2d.draw_text_centered("Elapsed time - " + ":".join(map(str, self._end_time)), (self._arena_width // 2, 150), constants.MEDIUM_FONT_SIZE)

    def get_time(self, date):        
        days, seconds = date.days, date.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        return hours, minutes, seconds

    def draw_text_rules(self, text, _type: int, width: int, height: int, font_size: int):
        g2d.set_color(constants.WHITE)
        
        if _type == 1:
            width *= 3

        for s in text:
            g2d.draw_text_centered(s, (width, height), font_size)
            height += 15

    def rules(self):
        g2d.clear_canvas()
        
        g2d.set_color(constants.BLACK)
        g2d.fill_rect((0, 0, self._arena_width, self._arena_height))
        g2d.draw_image_clip(self._sprite, (10, 5, 136, 81), (190, 25, 116, 69)) #Moon patrol logo
        
        width, height = self._arena_width // 2, 120
        
        if self._count_player == 0:
            self.draw_text_rules(self._game.rules(constants.SINGLE_PLAYER), 0, width // 2, height + 30, constants.MEDIUM_FONT_SIZE)
            self.draw_text_rules(self._game.rules(constants.MULTIPLAYER), 1, width // 2, height + 30, constants.MEDIUM_FONT_SIZE)
        else:            
            if self._count_player == 1:
                self.draw_text_rules(self._game.rules(constants.ROVER_1), 0, width, height, constants.MEDIUM_FONT_SIZE)
            
            elif self._count_player == 2:
                self.draw_text_rules(self._game.rules(constants.ROVER_1), 0, width // 2, height, constants.MEDIUM_FONT_SIZE)
                self.draw_text_rules(self._game.rules(constants.ROVER_2), 1, width // 2, height, constants.MEDIUM_FONT_SIZE)

            self.draw_text_rules(self._game.rules(constants.START_GAME), 0, width, 200, constants.MEDIUM_FONT_SIZE)

def gui_play(game: MoonPatrolGame):
    g2d.init_canvas(game.arena().size())
    ui = MoonPatrolGui(game)
    g2d.main_loop(ui.tick)
