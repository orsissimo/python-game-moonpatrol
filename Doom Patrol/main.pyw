'''@authors  Simone Orsi (305461) and Martina Gualtieri (308783)'''

from moonpatrolgui import gui_play
from moonpatrol import MoonPatrol
import constants

def main():
    configuration_file = "configuration_file.txt"
    game_rules_file = "game_rules.txt"
    
    game = MoonPatrol((constants.ARENA_WIDTH, constants.ARENA_HEIGHT), configuration_file, game_rules_file)
    gui_play(game)
    
main()  
