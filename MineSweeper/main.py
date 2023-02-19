# Minesweeper Game

"""
TODO:
change the safe radius of the first click in gen_field to 1 tile around it. FIX THIS. SOMETIMES THE SAFE ZONE ISNT THERE

sound effects when you clear a tile

show the number of mines left

[================== URGENT ==================]
Explosion animation sometimes starts at wrong frame:
so need to input the starting tick to the function or just input the correct tick.

Sometimes doesnt chord because thinks theres -ive unflagged mines
checks unflagged mines by looping through adjacent

[============================================]
"""

import pygame, random, os, csv, sys
from Button import Button

pygame.init()
pygame.mixer.init()
os.chdir(os.path.dirname(sys.argv[0]))

class Board():
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.dead = False

        #colours
        self.square_1 = ("#5DADE2", "#D6EAF8", "#F7DC6F")
        self.square_2 = ("", "", "")

        #difficulties
        attributes = [
        # [size, tile size, mines, font, font size]
        [8, 90, 10, pygame.font.SysFont(None, 130), 80],
        [16, 45, 50, pygame.font.SysFont(None, 65), 40],
        [24, 30, 99, pygame.font.SysFont(None, 45), 25]
        ]

        self.top_left = (120, 160)
        self.size = attributes[difficulty][0]
        self.tile_size = attributes[difficulty][1]
        self.mines = attributes[difficulty][2]
        self.num_font = attributes[difficulty][3]
        self.font_size = attributes[difficulty][4]

        #tiles
        self.top_tiles = [
        pygame.image.load(os.path.join("assets", "top1.png")).convert(),
        pygame.image.load(os.path.join("assets", "top2.png")).convert()]

        self.top_tiles[0] = pygame.transform.scale(self.top_tiles[0], (self.tile_size, self.tile_size))
        self.top_tiles[1] = pygame.transform.scale(self.top_tiles[1], (self.tile_size, self.tile_size))

        self.flag = pygame.transform.scale(flag_surf, (self.tile_size, self.tile_size))

        self.bomb = [pygame.transform.scale(frame, (self.tile_size*2, self.tile_size*2.4)) for frame in bomb]

        self.crater = pygame.transform.scale(crater, (self.tile_size, self.tile_size))

        self.numbers = [
        self.num_font.render("", True, "#FFFFFF"),
        self.num_font.render("1", True, "#3BD22F"),#green
        self.num_font.render("2", True, "#5DADE2"),#blue
        self.num_font.render("3", True, "#FFE400"),#yellow
        self.num_font.render("4", True, "#E74C3C"),#red
        self.num_font.render("5", True, "#A569BD"),#purple
        self.num_font.render("6", True, "#E55FE1"),#pink
        self.num_font.render("7", True, "#5FE5E5"),#cyan
        self.num_font.render("8", True, "#FDFEFE")#white
        ]

        self.uncleared = []
        for row in range(self.size):
            for tile in range(self.size):
                self.uncleared.append((row, tile))

        coord = lambda pos: (self.tile_size * pos[i] + self.top_left[i] for i in [0, 1])

        self.flagged_tiles = []
        self.flags = self.mines

        self.boomed = False

    def gen_field(self, first_click):
        size = self.size
        mines = self.mines

        row = ["." for i in range(size)]
        field = [list(row) for i in range(size)]

        first_y, first_x = first_click

        safe_zone = []

        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                safe_zone.append((first_y + y, first_x + x))

        i = 0
        while i < mines:
            rand_x = random.randint(0, size-1)
            rand_y = random.randint(0, size-1)
            if field[rand_y][rand_x] != "*":
                if (rand_y, rand_x) not in safe_zone:
                    field[rand_y][rand_x] = "*"
                    i += 1
        self.field = field

    def calc_field(self):
        field = self.field
        dim = [len(field), len(field[0])]

        for row_num, row in enumerate(field):
            for tile_num, tile in enumerate(row):
                if tile == ".":
                    field[row_num][tile_num] = 0

        for row_num, row in enumerate(field):
            for square_num, square in enumerate(row):
                if row[square_num] != "*":
                    # squares to the left
                    if square_num > 0:
                        if row[square_num - 1] == "*":
                            row[square_num] += 1
                        # squares to the top left
                        if row_num > 0:
                            if field[row_num - 1][square_num - 1] == "*":
                                row[square_num] += 1
                    # squares to the right
                    if square_num < dim[1] - 1:
                        if row[square_num + 1] == "*":
                            row[square_num] += 1
                        # squares to the bottom right
                        if row_num < dim[0] - 1:
                            if field[row_num + 1][square_num + 1] == "*":
                                row[square_num] += 1
                    # squares above
                    if row_num > 0:
                        if field[row_num - 1][square_num] == "*":
                            row[square_num] += 1
                        # squares to the top right
                        if square_num < dim[0] - 1:
                            if field[row_num - 1][square_num + 1] == "*":
                                row[square_num] += 1
                    # squares below
                    if row_num < dim[0] - 1:
                        if field[row_num + 1][square_num] == "*":
                            row[square_num] += 1
                        # squares to the bottom left
                        if square_num > 0:
                            if field[row_num + 1][square_num - 1] == "*":
                                row[square_num] += 1

        self.field = field

        # for row in self.field:
        #     print(list(map(str, row)))

    def clicked_tile(self, click_coord):
        x_pos = int((click_coord[0] - self.top_left[0])//self.tile_size)
        y_pos = int((click_coord[1] - self.top_left[1])//self.tile_size)
        # print(f"clicked_tile {y_pos} {x_pos}")
        return (y_pos, x_pos)

    def draw(self):
        #draw out the numbers.
        coord = lambda pos: tuple(self.tile_size * pos[i] + self.top_left[i] + (self.tile_size - self.font_size) + 0**i*self.tile_size/8 for i in [0, 1]) # get pixel coordinate for the number
        # coord = lambda pos: tuple(pos[i]*(i+1)*3**3 + self.top_left[i] for i in [0, 1]) # get pixel coordinate for the number

        for row_num, row in enumerate(self.field):
            for tile_num, tile in enumerate(row):
                if tile != "*":
                    screen.blit(self.numbers[tile], coord((tile_num, row_num)))

    def draw_cover(self):
        coord = lambda pos: tuple(self.tile_size * pos[i] + self.top_left[i] for i in [0, 1])
        for pos in self.uncleared:
            screen.blit(self.top_tiles[int((pos[0]+pos[1]))%2], coord(pos[::-1]))
            if pos in self.flagged_tiles:
                screen.blit(self.flag, [i for i in coord(pos[::-1])])

    def update(self, tile_pos):
        # print(f"updated {tile_pos}")
        tile = self.field[tile_pos[0]][tile_pos[1]]
        branches = [tile_pos]

        coord = lambda pos: (self.tile_size * dim + self.top_left for dim in pos)

        if tile_pos in self.uncleared:
            if tile == 0:
                #update all tiles around that aren't mines
                # if tile_pos in self.uncleared:
                self.uncleared.remove(tile_pos)
            elif tile == "*":
                if tile_pos in self.flagged_tiles:
                    return 0
                self.dead = True
                bruh_sound.play()
            else:
                #add the position to the cleared list
                self.uncleared.remove(tile_pos)

        changed = True
        while changed:
            changed = False
            for row_num, row in enumerate(self.field):
                for tile_num, tile in enumerate(row):
                    if tile == 0 and (row_num, tile_num) not in self.uncleared:
                        for x in [-1, 0, 1]:
                            for y in [-1, 0, 1]:
                                if (row_num + x, tile_num + y) in self.uncleared:
                                    self.uncleared.remove((row_num + x, tile_num + y))
                                    changed = True

        #Doesnt work. reveals everything around a 0 tile
        # zeros = [(zero[0] + x, zero[1] + y) for x in [-1, 0, 1] for y in [-1, 0, 1] for zero in self.uncleared if self.field[zero[0]][zero[1]] == 0]

        # for zero in zeros:
        #     if zero in self.uncleared:
        #         self.uncleared.remove(zero)

    def mark_flag(self, tile_pos):
        if tile_pos in self.flagged_tiles:
            self.flagged_tiles.remove(tile_pos)
            self.flags += 1
        elif tile_pos in self.uncleared:
            self.flagged_tiles.append(tile_pos)
            self.flags -= 1 #available flags for the counter

    def show_mines(self, tick):
        if not tick%14:
            #boomed is when its finished booming
            self.boomed = True
        #reveal all the mines when they blow up
        coord = lambda pos: [self.tile_size * dim + self.top_left[i] for i, dim in enumerate(pos)]
        for row_num, row in enumerate(self.field):
            for tile_num, tile in enumerate(row):
                if tile == "*":
                    if (row_num, tile_num) in self.uncleared:
                        screen.blit(self.crater, coord((tile_num, row_num)))
                        if not self.boomed:
                            screen.blit(self.bomb[tick//2%14], (coord((row_num, tile_num))[1]-self.tile_size*0.75, coord((row_num, tile_num))[0]-self.tile_size*1))

    def chord(self, tile_pos):
        chord_zone = []
        for y in [-1, 0, 1]:
            for x in [-1, 0, 1]:
                if (x, y) != (0, 0):
                    chord_zone.append((tile_pos[0] + y, tile_pos[1] + x))

        adjacent_mines = self.field[tile_pos[0]][tile_pos[1]]
        if isinstance(adjacent_mines, int):
            if adjacent_mines > 0:
                for pos in chord_zone:
                    if pos in self.flagged_tiles:
                        # print(f"{pos=}")
                        adjacent_mines -= 1

        # print(f"{adjacent_mines=}")

        if not adjacent_mines and tile_pos not in self.uncleared:
            #chordable
            for pos in chord_zone:
                if pos in self.uncleared and pos not in self.flagged_tiles:
                    # self.uncleared.remove(pos)
                    self.update(pos)

def boom():
    #unused
    bruh_sound.play()
    for i in range(31):
        screen.blit(explosion[i], explosion_rects[i])
        clock.tick(30)
        pygame.display.update()

# GUI
screen = pygame.display.set_mode((960, 960))

bg_shadow = pygame.Surface((960, 600))
bg_shadow.fill("#BCDDF3")

# Graphics
title_surf = pygame.image.load(os.path.join("assets", "Title.png")).convert_alpha()
title_rect = title_surf.get_rect(center = (480, 180))

score_rect = pygame.Rect(320, 85, 320, 60)
score_shadow = pygame.Rect(320, 95, 320, 60)

stats_rect = pygame.Rect(320, 300, 320, 200)
stats_shadow = pygame.Rect(320, 310, 320, 200)

clock_surf = pygame.image.load(os.path.join("assets", "clock.png")).convert_alpha()
clock_surf = pygame.transform.scale(clock_surf, (60, 60))
clock_rect = clock_surf.get_rect(topleft = (320, 85))

flag_surf = pygame.image.load(os.path.join("assets", "flag.png")).convert_alpha()
flag_surf = pygame.transform.scale(flag_surf, (60, 60))
flag_rect = flag_surf.get_rect(topleft = (520, 85))

# Explosion
explosion = [pygame.image.load(os.path.join("assets", "explosion", f"frame_{str(i)}.png")).convert_alpha() for i in range(31)]
explosion = [pygame.transform.scale(frame, (1900, 960)) for frame in explosion]
explosion_rects = [frame.get_rect(center = (480, 480)) for frame in explosion]
bruh_sound = pygame.mixer.Sound(os.path.join("assets", "bruh.mp3"))

# mine
bomb = [pygame.image.load(os.path.join("assets", "bomb", f"bomb{i}.png")).convert_alpha() for i in range(14)]

crater = pygame.image.load(os.path.join("assets", "crater.png")).convert_alpha()

pygame.display.set_caption("Mine Sweeper")

# Clock
clock = pygame.time.Clock()

# Text
font1 = pygame.font.SysFont("bahnschrift", 30)
font2 = pygame.font.SysFont("bahnschrift", 45)
font3 = pygame.font.SysFont("bahnschrift", 52)

ticks = 0
time = str(f"{round(ticks/60, 0)}")
timer = font2.render(time, True, "#34495E")

mines = 0

# Colours
white = "#FFFFFF"
button_top = "#2874A6"
button_bottom = "#1A5276"
button_change = "#85C1E9"

# text, text colour, width, height, pos, elevation, top colour, bottom colour, change colour, border radius
btnEasy = Button(font1, "Easy (8x8)", white, 300, 100, (15, 300), 10, button_top, button_bottom, button_change, 10)
btnMedium = Button(font1, "Medium (16x16)", white, 300, 100, (330, 300), 10, button_top, button_bottom, button_change, 10)
btnHard = Button(font1, "Hard (24x24)", white, 300, 100, (645, 300), 10, button_top, button_bottom, button_change, 10)

btnMenu = Button(font1, "Menu [ESC]", white, 200, 75, (40, 40), 12, "#E74C3C", "#943126", "#F1948A", 7)
btnRestart = Button(font1, "Restart [SPACE]", white, 250, 75, (670, 40), 12, "#E74C3C", "#943126", "#F1948A", 7)
btnQuit = Button(font1, "QUIT", white, 360, 125, (300, 640), 15, button_top, button_bottom, button_change, 15)

# menu function
def main_menu():
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btnEasy.check_click():
                    gamemode(0, 8)
                if btnMedium.check_click():
                    gamemode(1, 16)
                if btnHard.check_click():
                    gamemode(2, 24)
                if btnQuit.check_click():
                    pygame.quit()
                    sys.exit()

            screen.fill("#D6EAF8")
            screen.blit(bg_shadow, (0, 440))
            screen.blit(title_surf, title_rect)

            btnEasy.draw(screen)
            btnMedium.draw(screen)
            btnHard.draw(screen)

            btnQuit.draw(screen)

            pygame.display.update()
            clock.tick(60)

def gamemode(difficulty, size):
    run = True
    ticks = 0
    start_tick = 0
    start = False

    minefield = Board(difficulty)

    base_surfs = []

    base_surfs.append(pygame.image.load(os.path.join("assets", "8x8.png")).convert())
    base_surfs.append(pygame.image.load(os.path.join("assets", "16x16.png")).convert())
    base_surfs.append(pygame.image.load(os.path.join("assets", "24x24.png")).convert())
    base = base_surfs[difficulty].get_rect(center = (480, 520))

    while run:
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    gamemode(difficulty, size)
                    run = False
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btnMenu.check_click():
                    main_menu()
                    run = False
                if btnRestart.check_click():
                    gamemode(difficulty, size)
                    run = False
                if base.collidepoint(pygame.mouse.get_pos()):
                    if not start:
                        start = True
                        minefield.gen_field(minefield.clicked_tile(pygame.mouse.get_pos()))
                        minefield.calc_field()
                        minefield.update(minefield.clicked_tile(pygame.mouse.get_pos()))
                        minefield.draw()
                    else:
                        if not (minefield.dead or len(minefield.uncleared) == minefield.mines):
                            if event.button == 1:
                                minefield.update(minefield.clicked_tile(pygame.mouse.get_pos()))
                                if pygame.mouse.get_pressed()[2]:
                                    minefield.chord(minefield.clicked_tile(pygame.mouse.get_pos()))
                            elif event.button == 3:
                                minefield.mark_flag(minefield.clicked_tile(pygame.mouse.get_pos()))
                                if pygame.mouse.get_pressed()[0]:
                                    minefield.chord(minefield.clicked_tile(pygame.mouse.get_pos()))
                            elif event.button == 2:
                                minefield.chord(minefield.clicked_tile(pygame.mouse.get_pos()))
                            minefield.draw()

        screen.fill("#D6EAF8")
        screen.blit(bg_shadow, (0, 480))
        btnMenu.draw(screen)
        btnRestart.draw(screen)

        if not minefield.dead: time = f"{str(int(ticks/60)).zfill(3)}"
        pygame.draw.rect(screen, "#1F618D", score_shadow, border_radius = 10)
        pygame.draw.rect(screen, "#5DADE2", score_rect, border_radius = 10)

        timer = font2.render(time, True, "#FFFFFF")
        flags_left = font2.render(str(minefield.flags), True, "#FFFFFF")
        screen.blit(timer, (385, 87))
        screen.blit(clock_surf, clock_rect)
        screen.blit(flag_surf, flag_rect)
        screen.blit(flags_left, (582, 87))
        screen.blit(base_surfs[difficulty], base)

        if start:
            minefield.draw()

        minefield.draw_cover()
        if len(minefield.uncleared) == minefield.mines:
            # print(f"you win with a time of {ticks/60:.1f}")
            pygame.draw.rect(screen, "#85C1E9", stats_shadow, border_radius = 10)
            pygame.draw.rect(screen, "#5DADE2", stats_rect, border_radius = 10)
            screen.blit(score_surf, (376, 350))
        else:
            ticks += 1
            score = int(ticks/60//1)
            score_surf = font2.render(f"Score: {str(score).zfill(3)}", True, "#FFFFFF")

        if minefield.dead:
            minefield.show_mines(ticks-start_tick)
        else:
            start_tick = ticks

        clock.tick(60)

if __name__ == "__main__":
    main_menu()
