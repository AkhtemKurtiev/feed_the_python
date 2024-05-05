from random import choice, randint
from typing import Union, Optional

import pygame

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
SIDE = (UP, DOWN, LEFT, RIGHT)

TURNS = {
    (pygame.K_UP, DOWN): UP,
    (pygame.K_DOWN, UP): DOWN,
    (pygame.K_LEFT, RIGHT): LEFT,
    (pygame.K_RIGHT, LEFT): RIGHT,
}

BOARD_BACKGROUND_COLOR = (0, 0, 0)
CONTOUR_COLOR = (93, 216, 228)
CONTOUR_WIDTH = 1

HEAD_AND_NECK = 2

SPEED = 5

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

pygame.display.set_caption('Змейка')

clock = pygame.time.Clock()


class GameObject():
    """Базовый класс, от которого наследуются другие игровые объекты."""

    def __init__(self) -> None:
        self.position: Union[tuple, list] = ((GRID_WIDTH // 2),
                                             (GRID_HEIGHT // 2))
        self.body_color: tuple = (0, 0, 0)

    def draw(self, *args, **kwargs):
        """Предназначен для переопределения в дочерних классах.
        Этот метод должен определять,
        как объект будет отрисовываться на экране.
        """
        raise NotImplementedError("Method not implemented!")


class Apple(GameObject):
    """Класс унаследованный от GameObject,
    описывающий яблоко и действия c ним.
    """

    def __init__(self) -> None:
        super().__init__()
        self.body_color: tuple = (255, 0, 0)
        self.position: tuple = (0, 0)

    def randomize_position(self) -> None:
        """Устанавливает случайное положение яблока на игровом поле."""
        width = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        height = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (width, height)

    def draw(self, surface):
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, CONTOUR_COLOR, rect, CONTOUR_WIDTH)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    length: int = 1
    positions: list = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]

    def __init__(self) -> None:
        super().__init__()
        self.length = Snake.length
        self.positions = Snake.positions
        self.direction: tuple = RIGHT
        self.next_direction: Optional[tuple] = None
        self.body_color: tuple = (0, 255, 0)
        self.last: Optional[tuple] = None

    def update_direction(self) -> None:
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию змейки."""
        head = Snake.get_head_position(self)
        new_width = head[0] + self.direction[0] * 20
        new_height = head[1] + self.direction[1] * 20

        new_head = new_width, new_height

        if new_head[0] > SCREEN_WIDTH:
            new_head = 0, new_head[1]
        elif new_head[1] > SCREEN_HEIGHT:
            new_head = new_head[0], 0
        elif new_head[0] < 0:
            new_head = SCREEN_WIDTH, new_head[1]
        elif new_head[1] < 0:
            new_head = new_head[0], SCREEN_HEIGHT

        self.positions.insert(0, new_head)

    def draw(self, surface):
        """Отрисовывает змейку на экране, затирая след."""
        for position in self.positions[:-1]:
            rect = (
                pygame.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, CONTOUR_COLOR, rect, CONTOUR_WIDTH)

        head = self.positions[0]
        head_rect = pygame.Rect((head[0], head[1]), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, CONTOUR_COLOR, head_rect, CONTOUR_WIDTH)

        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние
        после столкновения с собой.
        """
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = choice(SIDE)
        self.next_direction = None
        self.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object) -> None:
    """Обрабатывает нажатия клавиш,
    чтобы изменить направление движения змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            for (status, side), res_side in TURNS.items():
                if event.key == status and game_object.direction != side:
                    game_object.next_direction = res_side
                    break


def main():
    """Логика игры."""
    snake = Snake()
    apple = Apple()
    apple.randomize_position()
    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.positions[0] == apple.position:
            snake.length += 1
            apple.randomize_position()

        if len(snake.positions) > snake.length:
            snake.last = snake.positions[-1]
            snake.positions.pop()

        if (len(snake.positions) > HEAD_AND_NECK
                and snake.positions[0] in snake.positions[2:]):
            snake.reset()
            apple.randomize_position()

        apple.draw(screen)
        snake.draw(screen)

        pygame.display.update()


if __name__ == '__main__':
    main()
