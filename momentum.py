import pygame
import math
from random import randint

WINDOW_SCALE = (600, 600)
screen = pygame.display.set_mode(WINDOW_SCALE)

FPS = 60
WHITE = (255, 255, 255)
static_ball_counter = 0


class Ball(pygame.sprite.Sprite):
    def __init__(self, radius=None, color=None, spawn_point=None, debug_mode=False):
        super().__init__()

        global static_ball_counter
        self.id = static_ball_counter
        static_ball_counter += 1
        self.velocity = [0.0, 0.0]
        self.speed = 0
        self.collision_cooldown = 5
        self.debug_mode = debug_mode
        self.is_colliding = False

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
        self.speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)

    def get_momentum(self):
        return [self.velocity[0]*self.mass, self.velocity[1]*self.mass]

    def set_zero_speed(self):
        self.velocity = [0, 0]
        self.speed = 0

    def update(self):
        print('ball num:', self.id, 'position', [self.x, self.y], 'velocity:', self.velocity)
        self.collision_cooldown -= 1
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.check_collision()

    def check_collision(self):
        horizontal_flip = (self.x - self.radius < 0 and self.velocity[0] < 0) or \
            (self.x + self.radius > WINDOW_SCALE[0] and self.velocity[0] > 0)
        vertical_flip = (self.y - self.radius < 0 and self.velocity[1] < 0) or \
            (self.y + self.radius > WINDOW_SCALE[1] and self.velocity[1] > 0)
        if horizontal_flip:
            self.velocity[0] *= -1
        if vertical_flip:
            self.velocity[1] *= -1
        if horizontal_flip or vertical_flip:
            self.is_colliding = True
        if not horizontal_flip and not vertical_flip:
            self.is_colliding = False

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

        if self.debug_mode:
            pygame.draw.line(screen, (255, 0, 0), (self.x, self.y),
                             (self.x + self.velocity[0] * 10, self.y + self.velocity[1] * 50), 2)


class Ball_To_Ball_Interaction:
    def __init__(self, first_ball: Ball, second_ball: Ball, decay_rate):
        self.first_ball = first_ball
        self.second_ball = second_ball
        self.min_distance = first_ball.radius + second_ball.radius
        self.offset = 3
        self.consecutive_call_counter = 0
        self.decay_rate = decay_rate

        self.small_ball, self.big_ball = second_ball, first_ball
        if first_ball.mass < second_ball.mass:
            self.small_ball, self.big_ball = first_ball, second_ball

    def update_interaction(self):
        self.distance = get_distance_between_two_balls(
            self.first_ball, self.second_ball)
        self.direction_between = (
            self.second_ball.x - self.first_ball.x, self.second_ball.y - self.first_ball.y)

    def check_collision(self):
        if self.distance < (self.min_distance + self.offset):
            self.first_ball.is_colliding = True
            self.second_ball.is_colliding = True
            self.bounce_opposite_directions()
        else:
            self.first_ball.is_colliding= True
            self.second_ball.is_colliding = True
            self.consecutive_call_counter = 0

    def bounce_opposite_directions(self):
        if self.consecutive_call_counter > 1:
            #print('block collision')
            return

        if self.consecutive_call_counter == 1:
            self.small_ball.velocity = [
                -self.small_ball.velocity[0], -self.small_ball.velocity[1]]
            self.consecutive_call_counter += 1
            #print('flip small velocity')
            return

        #print('first collision:\n')
        #print('small ball velocity before:', self.small_ball.velocity)
        #print('big ball velocity before:', self.big_ball.velocity)

        big_momentum = self.first_ball.get_momentum().copy()
        small_momentum = self.second_ball.get_momentum().copy()

        # decay energy
        big_momentum = vector_multiplication(big_momentum, self.decay_rate)
        small_momentum = vector_multiplication(small_momentum, self.decay_rate)

        self.first_ball.set_zero_speed()
        self.first_ball.add_force(small_momentum)

        self.second_ball.set_zero_speed()
        self.second_ball.add_force(big_momentum)

        #print('\nsmall ball velocity after:', self.small_ball.velocity)
        #print('big ball velocity after:', self.big_ball.velocity)

        self.consecutive_call_counter += 1


def vector_addition(vector1, vector2):
    return [vector1[0]+vector2[0], vector1[1]+vector2[1]]


def vector_multiplication(vector, multiply):
    return [vector[0]*multiply, vector[1]*multiply]


def get_distance_between_two_balls(first_ball, second_ball):
    return math.sqrt(math.pow(first_ball.x - second_ball.x, 2) + math.pow(first_ball.y - second_ball.y, 2))


class Plane:
    def __init__(self, amount=None, speed=None, radius=None, randomize_radius=False, decay_rate=1, gravity_scale=0):
        self.decay_rate = decay_rate
        self.gravity_vector = vector_multiplication([0,1], gravity_scale)
        if amount is None:
            self.balls: list[Ball] = []
            self.ball_interactions: list[Ball_To_Ball_Interaction] = []
            return

        if randomize_radius:
            self.balls = [Ball(randint(10, radius)) for x in range(amount)]

        else:
            self.balls = [Ball(radius) for x in range(amount)]
        [ball.add_force((randint(-speed, speed),
                        randint(-speed, speed))) for ball in self.balls]

        self.ball_interactions: list[Ball_To_Ball_Interaction] = []
        for i in range(len(self.balls)):
            for j in range(i+1, len(self.balls)):
                interaction = Ball_To_Ball_Interaction(
                    self.balls[i], self.balls[j], decay_rate=self.decay_rate)
                self.ball_interactions.append(interaction)

    def add_ball(self, ball):
        self.balls.append(ball)

        self.ball_interactions: list[Ball_To_Ball_Interaction] = []
        for i in range(len(self.balls)):
            for j in range(i+1, len(self.balls)):
                interaction = Ball_To_Ball_Interaction(
                    self.balls[i], self.balls[j], decay_rate=self.decay_rate)
                self.ball_interactions.append(interaction)

    def update_screen(self):
        screen.fill((0, 0, 0))
        print()
        for interaction in self.ball_interactions:
            interaction.update_interaction()
            interaction.check_collision()

        for ball in self.balls:
            ball.update()
            if ball.y < WINDOW_SCALE[1]-ball.radius and not ball.is_colliding:
                ball.add_force(self.gravity_vector)
            ball.draw()
        pygame.display.update()


def three_size_ball_plane():
    plane = Plane()
    small_ball = Ball(10, spawn_point=(10, 10))
    small_ball.add_force((10, -10))
    big_ball = Ball(60, spawn_point=(300, 300))
    big_ball.add_force((10, -10))
    medium_ball = Ball(20, spawn_point=(50, 50))
    medium_ball.add_force((-2, -2))
    plane.add_ball(small_ball)
    plane.add_ball(medium_ball)
    plane.add_ball(big_ball)
    return plane


def one_big_ball_plane():
    plane = Plane(20, 20, 20, True)
    big_ball = Ball(50, spawn_point=(100, 100))
    big_ball.add_force((100, -100))
    plane.add_ball(big_ball)
    return plane


def small_particles_plane():
    plane = Plane(100, 20, 10)
    return plane


def main():
    pygame.init()
    clock = pygame.time.Clock()
    run = True
    plane = Plane(7, 20, 20, True, 0.8, 3)
    while (run):
        global FPS
        clock.tick(FPS)

        plane.update_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if FPS < 150:
                        FPS += 15
                if event.key == pygame.K_DOWN:
                    if FPS > 15:
                        FPS -= 15


if __name__ == '__main__':
    main()
