import pygame
from random import randint

WINDOW_SCALE = (600, 600)
screen = pygame.display.set_mode(WINDOW_SCALE)


class Ball(pygame.sprite.Sprite):
    def __init__(self, radius=None, color=None, spawn_point=None):
        super().__init__()

        self.velocity = [0.0, 0.0]

        if radius:
            self.radius = radius
        else:
            self.radius = randint(10, 30)

        self.mass = self.radius

        if color:
            self.color = color
        else:
            self.color = (randint(0, 255), randint(0, 255), randint(0, 255))

        if spawn_point:
            self.x, self.y = spawn_point[0], spawn_point[1]
        else:
            self.x = randint(self.radius, WINDOW_SCALE[0]-self.radius)
            self.y = randint(self.radius, WINDOW_SCALE[1]-self.radius)

        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def add_force(self, force):
        self.velocity[0] += force[0] / self.mass
        self.velocity[1] += force[1] / self.mass

    def update_position(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


class Plane:
    def __init__(self):
        self.balls = [Ball() for x in range(10)]
        [ball.add_force((randint(-3, 3), randint(-3, 3)))
         for ball in self.balls]

    def update_screen(self):
        screen.fill((0, 0, 0))
        self.check_collisions()

        for ball in self.balls:
            ball.update_position()
            ball.draw()
        pygame.display.update()

    def check_collisions(self):
        for ball in self.balls:
            horizontal_flip = ball.x - ball.radius < 0 or ball.x + \
                ball.radius > WINDOW_SCALE[0]
            vertical_flip = ball.y - ball.radius < 0 or ball.y + \
                ball.radius > WINDOW_SCALE[1]

            print(horizontal_flip, vertical_flip)
            if horizontal_flip:
                ball.velocity[0] *= -1
            if vertical_flip:
                ball.velocity[1] *= -1


def main():
    pygame.init()
    clock = pygame.time.Clock()
    run = True
    plane = Plane()
    while (run):
        clock.tick()
        plane.update_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


if __name__ == '__main__':
    main()
