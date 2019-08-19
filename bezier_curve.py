import sys

import pygame as p


# Pygame expects sequences as points when drawing, and I want to address x and y properties easily
class Point(list):
    def __init__(self, x, y, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.append(x)
        self.append(y)

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value


def bezier_curve(points):
    curve_points = []

    for t in range(101):
        t *= 0.01
        curve_points.append(bezier_point(points, t))

    return curve_points


def bezier_point(points, t):
    if len(points) == 1:
        return points[0]

    new_points = []

    for point1, point2 in zip(points, points[1:]):
        new_points.append(bezier_linear(point1, point2, t))

    return bezier_point(new_points, t)


def bezier_linear(point1, point2, t):
    x_diff = point2.x - point1.x
    y_diff = point2.y - point1.y
    return Point(point1.x + x_diff * t, point1.y + y_diff * t)


p.init()
POINT_RADIUS = 10
MAX_POINTS = 30
WIDTH = 1280
HEIGHT = 720
SIZE = WIDTH, HEIGHT
screen = p.display.set_mode(SIZE)
p.display.set_caption('Bezier Curve')

points = []

font = p.font.SysFont("Arial", 16)
big_font = p.font.SysFont("Arial", 32)
captions = []

for i in range(MAX_POINTS):
    caption = font.render(str(i + 1), True, (255, 255, 255))
    captions.append(caption)

help_text = [
    font.render("h - show/hide help", True, (255, 255, 255)),
    font.render("s - show/hide skeleton", True, (255, 255, 255)),
    font.render("l - show/hide lines", True, (255, 255, 255)),
    font.render("x - clear points", True, (255, 255, 255)),
    font.render("left/right arrows - decrease/increase 't'", True, (255, 255, 255))
]

help_text_width = int(max(l.get_width() for l in help_text))
help_text_height = int(max(l.get_height() for l in help_text))

point_under_cursor = None
left_pressed = False
right_pressed = False
t = 0.25
show_skeleton = False
show_lines = False
show_help = True


def bezier_point_draw(points, t, level=0):
    if len(points) == 1:
        x = int(points[0].x)
        y = int(points[0].y)
        p.draw.circle(screen, (255, 0, 0), (x, y), 4)
        return

    new_points = []

    for point1, point2 in zip(points, points[1:]):
        x1 = int(point1.x)
        y1 = int(point1.y)
        x2 = int(point2.x)
        y2 = int(point2.y)

        p.draw.aaline(screen, (0, 0, 255), (x1, y1), (x2, y2))

        color = 127, 255 * (MAX_POINTS - level) // MAX_POINTS, 0

        p.draw.circle(screen, color, (x1, y1), POINT_RADIUS // 2)
        p.draw.circle(screen, color, (x2, y2), POINT_RADIUS // 2)

        new_points.append(bezier_linear(point1, point2, t))

    return bezier_point_draw(new_points, t, level + 1)


def update():
    screen.fill((0, 0, 0))

    if len(points) > 1:
        curve_points = bezier_curve(points)
        p.draw.aalines(screen, (127, 127, 0), False, curve_points)

    if show_skeleton:
        if len(points) > 1:
            bezier_point_draw(points, t)

    if show_lines and not show_skeleton:
        if len(points) > 1:
            p.draw.aalines(screen, (0, 0, 255), False, points)

    for point, caption in zip(points, captions):
        x = int(point.x)
        y = int(point.y)
        p.draw.circle(screen, (0, 0, 255), (x, y), POINT_RADIUS)
        screen.blit(caption, (x - caption.get_width() // 2,
                              y - caption.get_height() // 2))

    if show_skeleton:
        t_text = big_font.render("{:.5}".format(float(t)), True,
                                 (255, 255, 255))
        screen.blit(t_text, (0, 0))

    if show_help:
        for i, line in enumerate(help_text):
            screen.blit(line,
                        (WIDTH - help_text_width, i * help_text_height))

    p.display.flip()


while True:
    for event in p.event.get():
        if event.type == p.QUIT:
            p.quit()
            sys.exit(0)
        elif event.type == p.MOUSEBUTTONUP:
            point_under_cursor = None
        elif event.type == p.MOUSEBUTTONDOWN:
            x, y = p.mouse.get_pos()

            point_under_cursor = None

            for point in points:
                if (point.x - x) ** 2 + (
                        point.y - y) ** 2 <= POINT_RADIUS ** 2:
                    if p.mouse.get_pressed()[2]:
                        points.remove(point)
                    elif p.mouse.get_pressed()[0]:
                        point_under_cursor = point

                    break
            else:
                if len(points) < MAX_POINTS and p.mouse.get_pressed()[0]:
                    points.append(Point(x, y))
        elif event.type == p.KEYDOWN:
            if event.key == p.K_x:
                points = []
            elif event.key == p.K_LEFT:
                left_pressed = True
            elif event.key == p.K_RIGHT:
                right_pressed = True
            elif event.key == p.K_s:
                show_skeleton = not show_skeleton
            elif event.key == p.K_l:
                show_lines = not show_lines
            elif event.key == p.K_h:
                show_help = not show_help
            elif event.key == p.K_ESCAPE:
                p.quit()
                sys.exit(0)
        elif event.type == p.KEYUP:
            if event.key == p.K_LEFT:
                left_pressed = False
            elif event.key == p.K_RIGHT:
                right_pressed = False

    if show_skeleton:
        if left_pressed:
            t -= 0.001
            t = max(t, 0)

        if right_pressed:
            t += 0.001
            t = min(t, 1)

    if point_under_cursor is not None:
        x, y = p.mouse.get_pos()
        point_under_cursor.x = x
        point_under_cursor.y = y

    update()
