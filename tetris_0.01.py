from random import randrange as rand
import pygame
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QInputDialog

# начальные параметры
cell_size = 20
cols = 15
rows = 25
maxfps = 30

# цвета

colors = [
    (0, 0, 0),
    (205, 92, 92),
    (220, 20, 60),
    (255, 20, 147),
    (255, 69, 0),
    (255, 255, 0),
    (255, 105, 180),
    (147, 112, 219),
    (35, 35, 35)
]

colors2 = [
    (0, 0, 0),
    (30, 144, 255),
    (0, 255, 255),
    (173, 255, 47),
    (50, 205, 50),
    (0, 255, 127),
    (32, 178, 170),
    (0, 191, 255),
    (35, 35, 35)
]

# части тетриса
tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]


class Menu1(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('menu.ui', self)
        self.initUI()

    def initUI(self):
        self.b1.clicked.connect(self.start)
        #self.b2.clicked.connect(self.vibor)
        self.b3.clicked.connect(self.exite)

    def start(self):
        tetris = Tetris()
        self.close()
        tetris.run()

    def exite(self):
        self.close()


class Tetrissound():
    def begin(self):
        sound1 = pygame.mixer.Sound('sound/begin.wav')
        sound1.play()

    def move(self):
        sound1 = pygame.mixer.Sound('sound/move.wav')
        sound1.play()

    def rotate(self):
        sound1 = pygame.mixer.Sound('sound/rotate.wav')
        sound1.play()

    def fall(self):
        sound1 = pygame.mixer.Sound('sound/fall.wav')
        sound1.play()

    def lines_crash(self):
        sound1 = pygame.mixer.Sound('sound/lines_crash.wav')
        sound1.play()


def rotate_clockwise(shape):
    return [[shape[y][x]
             for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)]


def rotate_clockwise1(shape):
    return[list(reversed(col)) for col in zip(*shape)]


def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False


def remove_row(board, row):
    del board[row]
    return [[0 for i in range(cols)]] + board


def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1


def new_board():
    board = [[0 for x in range(cols)]
             for y in range(rows)]
    board += [[1 for x in range(cols)]]
    return board


class Tetris(object):
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(250, 25)
        self.width = cell_size * (cols + 6)
        self.height = cell_size * rows
        self.rlim = cell_size * cols
        self.bground_grid = [[8 if x % 2 == y % 2 else 8 for x in range(cols)] for y in range(rows)]

        self.default_font = pygame.font.Font(
            pygame.font.get_default_font(), 12)

        self.screen = pygame.display.set_mode((self.width, self.height))

        # блок мыши

        pygame.event.set_blocked(pygame.MOUSEMOTION)
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.init_game()

    def new_stone(self):
        self.stone = self.next_stone[:]
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.stone_x = int(cols / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if check_collision(self.board,
                           self.stone,
                           (self.stone_x, self.stone_y)):
            self.gameover = True

    def init_game(self):
        self.board = new_board()
        self.new_stone()
        self.level = 1
        self.score = 0
        self.lines = 0
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)

    def disp_msg(self, msg, topleft):
        x, y = topleft
        for line in msg.splitlines():
            self.screen.blit(
                self.default_font.render(
                    line,
                    False,
                    (255, 255, 255),
                    (0, 0, 0)),
                (x, y))
            y += 14

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image = self.default_font.render(line, False,
                                                 (255, 255, 255), (0, 0, 0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (
                self.width // 2 - msgim_center_x,
                self.height // 2 - msgim_center_y + i * 22))

    def draw_matrix(self, matrix, offset):
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        colors[val] if (self.lines // 5) % 2 == 0 else colors2[val],
                        pygame.Rect(
                            (off_x + x) *
                            cell_size,
                            (off_y + y) *
                            cell_size,
                            cell_size,
                            cell_size), 0)

    def add_cl_lines(self, n):
        linescores = [0, 40, 100, 300, 1200]
        self.lines += n
        self.score += linescores[n] * self.level
        if self.lines >= self.level * 5:
            self.level += 1
            newdelay = 1000 - 100 * (self.level - 1)
            newdelay = 100 if newdelay < 100 else newdelay
            pygame.time.set_timer(pygame.USEREVENT + 1, newdelay)

    def move(self, delta_x):
        if not self.gameover and not self.paused:
            Tetrissound().move()
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not check_collision(self.board,
                                   self.stone,
                                   (new_x, self.stone_y)):
                self.stone_x = new_x

    def quit(self):
        self.center_msg("Выход...")
        pygame.display.update()
        sys.exit()

    def drop(self, manual):
        if not self.gameover and not self.paused:
            if manual:
                self.score += 1
                Tetrissound().move()
            self.stone_y += 1
            if check_collision(self.board,
                               self.stone,
                               (self.stone_x, self.stone_y)):
                self.board = join_matrixes(
                    self.board,
                    self.stone,
                    (self.stone_x, self.stone_y))
                self.new_stone()
                cleared_rows = 0
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            Tetrissound().lines_crash()
                            self.board = remove_row(
                                self.board, i)
                            cleared_rows += 1
                            break
                    else:
                        break
                self.add_cl_lines(cleared_rows)
                return True
        return False

    def insta_drop(self):
        if not self.gameover and not self.paused:
            Tetrissound().fall()
            while (not self.drop(True)):
                pass

    def rotate_stone(self):
        er1 = [1, 2, 3]
        er2 = [1, 2, 3]
        n = 0
        n1 = 0
        if not self.gameover and not self.paused:
            Tetrissound().rotate()
            if self.stone_x >= (cols - 3):
                new_stone = rotate_clockwise1(self.stone)
            else:
                new_stone = rotate_clockwise(self.stone)
            if self.stone_x == 0:
                while check_collision(self.board, new_stone, (self.stone_x, self.stone_y)):
                    if n == 3:
                        break
                    self.stone_x += er1[n]
                    n += 1
            if self.stone_x == cols:
                while check_collision(self.board, new_stone, (self.stone_x, self.stone_y)):
                    if n1 == 3:
                        break
                    self.stone_x -= er2[n1]
                    n1 += 1

            if n != 3 and n1 != 3 and not check_collision(self.board, new_stone, (self.stone_x, self.stone_y)):
                self.stone = new_stone
            n = 0
            n1 = 0

    def toggle_pause(self):
        self.paused = not self.paused

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def run(self):
        key_actions = {
            'ESCAPE': self.quit,
            'LEFT': lambda: self.move(-1),
            'RIGHT': lambda: self.move(+1),
            'DOWN': lambda: self.drop(True),
            'UP': self.rotate_stone,
            'p': self.toggle_pause,
            'SPACE': self.start_game,
            'RETURN': self.insta_drop
        }

        self.gameover = False
        self.paused = False

        dont_burn_my_cpu = pygame.time.Clock()
        while 1:
            self.screen.fill((0, 0, 0))
            if self.gameover:
                self.center_msg("""Вы проиграли!\nВаши очки: %d
нажмите пробел чтобы начать заново""" % self.score)
            else:
                if self.paused:
                    self.center_msg("Пауза")
                else:
                    pygame.draw.line(self.screen,
                                     (255, 255, 255),
                                     (self.rlim + 1, 0),
                                     (self.rlim + 1, self.height - 1))
                    self.disp_msg("Следующая:", (
                        self.rlim + cell_size // 2,
                        2))
                    self.disp_msg("Очки: %d\nУровень: %d\
                    \nЛинии: %d\n\nУправление:\nВлево, Вправо:\n движение\nВверх:\n поворот\nВниз:"
                                  "\n падение\nEnter:\n мгновенное\n падение\n P:\n Пауза"
                                  % (self.score, self.level, self.lines),
                                  (self.rlim + cell_size // 2, cell_size * 5))
                    self.draw_matrix(self.bground_grid, (0, 0))
                    self.draw_matrix(self.board, (0, 0))
                    self.draw_matrix(self.stone,
                                     (self.stone_x, self.stone_y))
                    self.draw_matrix(self.next_stone,
                                     (cols + 1, 2))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.drop(False)
                elif event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_" + key):
                            key_actions[key]()

            dont_burn_my_cpu.tick(maxfps)


if __name__ == '__main__':
    #tetris = Tetris()
    #sound = Tetrissound()
    #sound.begin()
    #tetris.run()
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
