import pygame
import sys
import os
import random
import math
import numpy

# Ustawienie seed dla random do testów
game_seed = 10
game_seed_count = 0

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna gry
width, height = 1280, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("2D Car Game")

# Wczytanie obrazu auta
car_dimensions = (1702/55, 3509/55)
car_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "car.png"))
car_image = pygame.transform.scale(car_image, car_dimensions)
car_image = pygame.transform.rotate(car_image, 90)
car_rect = car_image.get_rect()
car_rect.center = (width // 2, height // 2)

# Wczytanie obrazu flagi mety
flags_dimensions = (2355/58, 3513/58)
flag_end_img = pygame.image.load(os.path.join(os.path.dirname(__file__), "flag_end_0.png"))
flag_end_img = pygame.transform.scale(flag_end_img, flags_dimensions)
flag_end = flag_end_img.get_rect()
flag_end.center = (width // 2, height // 2)


# Ustawienia auta
car_speed = 0  # Początkowa prędkość
car_max_speed = 5  # Maksymalna prędkość
car_acceleration = 0.1  # Współczynnik przyspieszenia
car_angle = 90
car_turn_factor = 3

# Ustawienia wyglądu
track_color = (0, 0, 0)
track_inside_color = (66, 66, 66)
track_width = 75
track_radius_round = 30
map_color = (255, 250, 245)
map_margin = 75

# Ustawienia gry
max_count_tracks = 2 # Ilość torów do przejścia
count_track = 0
ilosc_mid_pointow = 3
max_ilosc_mid_pointow = 7

# Flaga, czy gra jest uruchomiona
gra_uruchomiona = False
gra_ukonczona = False

# Główna pętla gry
clock = pygame.time.Clock()


# Dane toru
current_track = {
    "start_point_x": map_margin,
    "start_point_y": 0,
    "mid_points": [],
    "end_point_x": width - map_margin,
    "end_point_y": 0,
    "start_line": (0, 0, 0, 0),
    "end_line": (0, 0, 0, 0),
    "points": [],
    "middle_line_points": [],
    "test_points": [],
    "test_lines": [],
    "lines": [],
    "lines_round": [],
    "track_points": [],
    "track_check_sum": 0
}
# Klasa do obsługi licznika czasu
class Timer:
    def __init__(self):
        self.start_time = 0
        self.running = False
        self.freezed = False
        self.freezed_time = 0

    def start(self):
        self.start_time = pygame.time.get_ticks()
        self.running = True

    def stop(self):
        self.start_time = 0
        self.running = False
    
    def freeze(self):
        self.freezed = True
        self.freezed_time = pygame.time.get_ticks()

    def restart(self):
        self.start_time = pygame.time.get_ticks()

    def get_elapsed_time(self):
        if self.freezed:
            return self.freezed_time - self.start_time
        elif self.running:
            return pygame.time.get_ticks() - self.start_time
        else:
            return 0
# Tworzenie liczników czasu
timer_main = Timer()
timer_track = Timer()
# Funkcja konwertująca tekst w milisekundach na tekst czytelny
def convert_timers_to_text(timer):
    elapsed_time = timer.get_elapsed_time()
    elapsed_seconds = elapsed_time // 1000
    elapsed_milliseconds = elapsed_time % 1000
    return f"{elapsed_seconds}.{round(elapsed_milliseconds/100)}s"
# Funkcja obliczająca odległość między punktami
def calculate_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
# Funkcja obliczająca środek między dwoma punktami
def middle_between_points(punkt1, punkt2):
    srodek_x = (punkt1[0] + punkt2[0]) / 2
    srodek_y = (punkt1[1] + punkt2[1]) / 2
    return (int(srodek_x), int(srodek_y))
# Funkcja sprawdzająca czy dwie linie się przecinają
def czy_linie_sie_przecinaja(linia1, linia2):
    x1, y1, x2, y2 = linia1
    x3, y3, x4, y4 = linia2

    def orientation(p, q, r):
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0:
            return 0  # Linie są współliniowe
        return 1 if val > 0 else 2  # 1 - zgodnie z ruchem wskazówek zegara, 2 - przeciwnie do ruchu wskazówek zegara

    def on_segment(p, q, r):
        return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
                q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))

    o1 = orientation((x1, y1), (x2, y2), (x3, y3))
    o2 = orientation((x1, y1), (x2, y2), (x4, y4))
    o3 = orientation((x3, y3), (x4, y4), (x1, y1))
    o4 = orientation((x3, y3), (x4, y4), (x2, y2))

    # Sprawdzenie ogólnego przypadku
    if o1 != o2 and o3 != o4:
        return True

    # Sprawdzenie szczególnego przypadku, gdy linie leżą na jednej prostej
    if o1 == 0 and on_segment((x1, y1), (x3, y3), (x2, y2)):
        return True
    if o2 == 0 and on_segment((x1, y1), (x4, y4), (x2, y2)):
        return True
    if o3 == 0 and on_segment((x3, y3), (x1, y1), (x4, y4)):
        return True
    if o4 == 0 and on_segment((x3, y3), (x2, y2), (x4, y4)):
        return True

    return False
# Funkcja obliczająca punkty przecięcia
def znajdz_punkt_przeciecia(linia1, linia2):
    x1, y1, x2, y2 = linia1
    x3, y3, x4, y4 = linia2

    # Obliczanie współczynnika nachylenia i przesunięcia dla obu linii
    a1 = (y2 - y1) / (x2 - x1) if x2 - x1 != 0 else float('inf')
    b1 = y1 - a1 * x1

    a2 = (y4 - y3) / (x4 - x3) if x4 - x3 != 0 else float('inf')
    b2 = y3 - a2 * x3

    # Sprawdzenie, czy linie są równoległe
    if a1 == a2:
        return None  # Linie są równoległe, brak punktu przecięcia

    # Obliczanie współrzędnych punktu przecięcia
    x = (b2 - b1) / (a1 - a2)
    y = a1 * x + b1

    return x, y
# Funkcja do rysowania półkola
def draw_semicircle(surface, center, point1, point2, color):
    radius = calculate_distance(center, point1)

    # Obliczenia kątów (w radianach) na podstawie punktów
    angle1 = pygame.math.Vector2(point1[0] - center[0], point1[1] - center[1]).angle_to(pygame.math.Vector2(1, 0))
    angle2 = pygame.math.Vector2(point2[0] - center[0], point2[1] - center[1]).angle_to(pygame.math.Vector2(1, 0))
    
    # Zamiana miejscami wartości kątów
    angle1, angle2 = angle2, angle1

    # Rysowanie półkola
    pygame.draw.arc(surface, color, (center[0] - radius, center[1] - radius, 2 * radius+2, 2 * radius+2), angle1/57, angle2/57, 5)
# Funkcja rysująca zaokrąglone linie toru
def draw_rounded_line(surface, color, start, end, radius):
    dx, dy = end[0] - start[0], end[1] - start[1]
    dist = math.hypot(dx, dy)

    if dist == 0:
        return  # Unikaj dzielenia przez zero

    dx /= dist
    dy /= dist

    rounded_start = (int(start[0] + radius * dx), int(start[1] + radius * dy))
    rounded_end = (int(end[0] - radius * dx), int(end[1] - radius * dy))

    pygame.draw.line(surface, color, rounded_start, rounded_end, 5)
# Funkcja rysująca przerywaną linię
def draw_dashed_line(surface, color, start_pos, end_pos, width=1, dash_length=10):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dl = dash_length

    if (x1 == x2):
        ycoords = [y for y in range(y1, y2, dl if y1 < y2 else -dl)]
        xcoords = [x1] * len(ycoords)
    elif (y1 == y2):
        xcoords = [x for x in range(x1, x2, dl if x1 < x2 else -dl)]
        ycoords = [y1] * len(xcoords)
    else:
        a = abs(x2 - x1)
        b = abs(y2 - y1)
        c = round(math.sqrt(a**2 + b**2))
        dx = dl * a / c
        dy = dl * b / c

        xcoords = [x for x in numpy.arange(x1, x2, dx if x1 < x2 else -dx)]
        ycoords = [y for y in numpy.arange(y1, y2, dy if y1 < y2 else -dy)]

    next_coords = list(zip(xcoords[1::2], ycoords[1::2]))
    last_coords = list(zip(xcoords[0::2], ycoords[0::2]))
    for (x1, y1), (x2, y2) in zip(next_coords, last_coords):
        start = (round(x1), round(y1))
        end = (round(x2), round(y2))
        pygame.draw.line(surface, color, start, end, width)
# Funkcja tworząca tekst
default_font_size = 36
default_text_color = (20, 20, 20)
def draw_text(screen, text, x, y, font_size=default_font_size, text_color=default_text_color):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)
# Funkcja od generowania toru
def generate_track(number_of_mid_points=1):
    global current_track, track_width, track_radius_round
    global width, height, map_margin
    global car_rect, car_angle, car_speed
    global count_track
    global game_seed, game_seed_count

    # Ustawianie nowego seeda
    game_seed_count += 1
    random.seed(game_seed + game_seed_count)
    print("---")
    print(f"Nowy seed: {game_seed + game_seed_count} [+{game_seed_count}]")

    # Resetowanie ustawień
    current_track["test_points"] = []
    current_track["track_points"] = []
    current_track["test_lines"] = []
    current_track["middle_line_points"] = []
    current_track["mid_points"] = []
    current_track["lines"] = []
    current_track["lines_round"] = []
    current_track["points"] = []
    current_track["start_line"] = (0, 0, 0, 0)
    current_track["end_line"] = (0, 0, 0, 0)
    current_track["track_check_sum"] = 0
    if timer_track.running:
        timer_track.restart()
    else:
        timer_track.start()
    count_track += 1

    # Losowanie punktu startu i mety
    current_track["start_point_y"] = random.randint(int(height/2-map_margin*2), int(height/2+map_margin*2))
    current_track["end_point_y"] = random.randint(int(height/2-map_margin*2), int(height/2+map_margin*2))

    # Losowanie ilości punktów środkowych
    mid_points = []
    mid_points.append((current_track["start_point_x"], current_track["start_point_y"])) # Start
    #
    gap = (width - map_margin*2) / number_of_mid_points
    #
    for i in range(number_of_mid_points):
        x = random.randint(int(mid_points[-1][0]) + map_margin*2, int(mid_points[-1][0]+gap))
        y = random.randint(map_margin, height-map_margin)
        mid_points.append((x, y))
    #
    mid_points.append((current_track["end_point_x"], current_track["end_point_y"])) # End

    # Wartość kroku (długość linii)
    step = 10

    # Tworzenie punktów toru
    for i in range(len(mid_points)-1):
        current_distance = calculate_distance(mid_points[i], mid_points[i + 1])
        num_segments = int(current_distance / step)

        # Obliczanie współczynników kierunkowych
        dx_mid = (mid_points[i + 1][0] - mid_points[i][0]) / num_segments
        dy_mid = (mid_points[i + 1][1] - mid_points[i][1]) / num_segments

        # Generowanie współrzędnych linii z odchyleniami
        for j in range(num_segments):
            if j == 0 or (j == num_segments-1 and i == len(mid_points)-2): # Tworzenie tylko pierwszego i ostatniego punktu # j == num_segments-1 or j == 0
                line_x = mid_points[i][0] + j * dx_mid
                line_y = mid_points[i][1] + j * dy_mid
                current_track["points"].append((int(line_x), int(line_y)))
    
    # Tworzenie linii toru
    for i in range(len(current_track["points"]) - 1):
        point1 = current_track["points"][i]
        point2 = current_track["points"][i + 1]

        # Obliczanie współczynników kierunkowych
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Normalizacja wektora kierunkowego
        dx /= distance
        dy /= distance

        # Obliczanie punktów leżących równolegle po obu stronach toru
        offset = track_width  # Grubość toru
        left_point = (point1[0] - offset * dy, point1[1] + offset * dx)
        left_point2 = (point2[0] - offset * dy, point2[1] + offset * dx)
        right_point = (point1[0] + offset * dy, point1[1] - offset * dx)
        right_point2 = (point2[0] + offset * dy, point2[1] - offset * dx)

        # Sprawdzanie czy linie się przecinają
        if i > 0:
            # PRAWA
            linia1 = current_track["lines"][-1]
            linia2 = (int(right_point[0]), int(right_point[1]), int(right_point2[0]), int(right_point2[1]))
            if czy_linie_sie_przecinaja(linia1, linia2):
                punkt_przeciecia = znajdz_punkt_przeciecia(linia1, linia2)
                right_point = punkt_przeciecia
                current_track["lines"][-1] = (current_track["lines"][-1][0], current_track["lines"][-1][1], punkt_przeciecia[0], punkt_przeciecia[1])
            # LEWA
            linia3 = current_track["lines"][-2]
            linia4 = (int(left_point[0]), int(left_point[1]), int(left_point2[0]), int(left_point2[1]))
            if czy_linie_sie_przecinaja(linia3, linia4):
                punkt_przeciecia = znajdz_punkt_przeciecia(linia3, linia4)
                left_point = punkt_przeciecia
                current_track["lines"][-2] = (current_track["lines"][-2][0], current_track["lines"][-2][1], punkt_przeciecia[0], punkt_przeciecia[1])
        
        # Obliczanie odległości pomiędzy końcami, jeśli są zbyt duże to uśrednienie ich
        if i > 0:
            # PRAWA
            point1 = (current_track["lines"][-1][2], current_track["lines"][-1][3])
            point2 = (right_point[0], right_point[1])
            dystans_pomiedzy = calculate_distance(point1, point2)
            if dystans_pomiedzy > 0:
                punkt_srodkowy = middle_between_points(point1, point2)
                current_track["lines"][-1] = (current_track["lines"][-1][0], current_track["lines"][-1][1], punkt_srodkowy[0], punkt_srodkowy[1])
                right_point = punkt_srodkowy
            # LEWA
            point3 = (current_track["lines"][-2][2], current_track["lines"][-2][3])
            point4 = (left_point[0], left_point[1])
            dystans_pomiedzy = calculate_distance(point3, point4)
            if dystans_pomiedzy > 0:
                punkt_srodkowy = middle_between_points(point3, point4)
                current_track["lines"][-2] = (current_track["lines"][-2][0], current_track["lines"][-2][1], punkt_srodkowy[0], punkt_srodkowy[1])
                left_point = punkt_srodkowy

        # Dodawanie punktów do listy
        current_track["lines"].append((int(left_point[0]), int(left_point[1]), int(left_point2[0]), int(left_point2[1])))
        current_track["lines"].append((int(right_point[0]), int(right_point[1]), int(right_point2[0]), int(right_point2[1])))

    # Sprawdzenie wszystkich linii czy nie są zbyt blisko siebie
    for i in range(2, len(current_track["lines"])-1, 2):
        punkt1 = (current_track["lines"][i][2], current_track["lines"][i][3])
        punkt2 = (current_track["lines"][i+1][2], current_track["lines"][i+1][3])
        if calculate_distance(punkt1, punkt2) < track_width*2-10:
            return generate_track(number_of_mid_points)

    # Zaokrąglenie toru
    for i in range(len(current_track["lines"])):
        start = (current_track["lines"][i][0], current_track["lines"][i][1])
        end = (current_track["lines"][i][2], current_track["lines"][i][3])

        dx, dy = end[0] - start[0], end[1] - start[1]
        dist = math.hypot(dx, dy)

        if dist == 0:
            return

        dx /= dist
        dy /= dist

        rounded_start = (int(start[0] + track_radius_round * dx), int(start[1] + track_radius_round * dy))
        rounded_end = (int(end[0] - track_radius_round * dx), int(end[1] - track_radius_round * dy))

        # Jeśli 2 pierwsze lub 2 ostatnie linie to ich nie zmniejszać
        if i < 2: # 2 pierwsze linie
            rounded_start = (int(start[0]), int(start[1]))
        if i >= len(current_track["lines"])-2: # 2 ostatnie linie
            rounded_end = (int(end[0]), int(end[1]))

        current_track["lines_round"].append(rounded_start + rounded_end)

    # Ustawianie lini startu i mety
    current_track["start_line"] = (
        current_track["lines"][0][0]-5,
        current_track["lines"][0][1],
        current_track["lines"][1][0]-5,
        current_track["lines"][1][1]
    )
    current_track["end_line"] = (
        current_track["lines"][-1][2],
        current_track["lines"][-1][3],
        current_track["lines"][-2][2],
        current_track["lines"][-2][3]
    )
    
    # Tworzenie punktów toru
    for line in current_track["lines"]:
        current_track["track_points"].append((line[0], line[1]))
        current_track["track_points"].append((line[2], line[3]))

    # Tworzenie punktów do środkowej lini przerywanej
    for i in range(0, len(current_track["lines"])-1, 2):
        middle_point = middle_between_points(
            (current_track["lines"][i][0], current_track["lines"][i][1]),
            (current_track["lines"][i+1][0], current_track["lines"][i+1][1])
        )
        current_track["middle_line_points"].append(middle_point)
        if i == len(current_track["lines"])-2: # Jeśli ostatni punkt to dodatkowo dla lini mety
            middle_point = middle_between_points(
                (current_track["lines"][i][2], current_track["lines"][i][3]),
                (current_track["lines"][i+1][2], current_track["lines"][i+1][3])
            )
            current_track["middle_line_points"].append(middle_point)


    # Ustawianie auta na pozycji startu
    car_angle = -math.degrees(math.atan2(current_track["lines"][0][3] - current_track["lines"][0][1], current_track["lines"][0][2] - current_track["lines"][0][0]))
    car_rect.center = (current_track["start_point_x"], current_track["start_point_y"])
    car_speed = 0
    
    # Ustawienie flag
    flag_end.center = (current_track["end_point_x"], current_track["end_point_y"])
    
    # Obliczanie sumy kontrolnej toru
    for (x1, y1, x2, y2) in current_track["lines"]:
        current_track["track_check_sum"] += int(x1)
        current_track["track_check_sum"] += int(y1)
        current_track["track_check_sum"] += int(x2)
        current_track["track_check_sum"] += int(y2)
    suma_kontrolna = current_track["track_check_sum"]
    print(f"Suma kontrolna toru: {suma_kontrolna}")


# Główna pętla gry
while True:
    # Wypełnienie ekranu kolorem tła
    screen.fill(map_color)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Obsługa naciśnięcia klawisza
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE:
                timer_track.restart()
                gra_uruchomiona = True
            if event.key == pygame.K_r and gra_ukonczona: # Restart gry
                gra_uruchomiona = False
                gra_ukonczona = False
                game_seed_count = 0
                print("Ustawianie seeda na 0 #1")
                # generate_track(ilosc_mid_pointow)
                count_track = 0
                timer_main = Timer()

                


    # Ruch auta tylko jeśli gra jest uruchomiona
    if gra_uruchomiona:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and car_speed > 0:
            car_angle += car_turn_factor
        if keys[pygame.K_RIGHT] and car_speed > 0:
            car_angle -= car_turn_factor
        if keys[pygame.K_UP]:
            # Przyspieszenie auta
            car_speed = min(car_speed + car_acceleration, car_max_speed)
        else:
            # Hamowanie auta
            car_speed = max(0, car_speed - car_acceleration)

        # Uruchomienie timera i generowanie toru
        if not timer_main.running:
            timer_main.start()
            generate_track(ilosc_mid_pointow)

        # Sprawdzenie czy auto przekroczyło linie toru lub mety
        for line in [current_track["start_line"]] + current_track["lines"]:
            #
            car_center = (int(car_rect.x+car_rect.width/2), int(car_rect.y+car_rect.height/2))
            car_direction_point = (
                int(car_center[0] + car_rect.width/2*math.cos(math.radians(car_angle))),
                int(car_center[1] - car_rect.width/2*math.sin(math.radians(car_angle)))
            )
            if czy_linie_sie_przecinaja(line, car_center+car_direction_point):
                car_angle = -math.degrees(math.atan2(current_track["lines"][0][3] - current_track["lines"][0][1], current_track["lines"][0][2] - current_track["lines"][0][0]))
                car_rect.center = (current_track["start_point_x"], current_track["start_point_y"])
                car_speed = 0
            # META
            if czy_linie_sie_przecinaja(current_track["end_line"], car_center+car_direction_point):
                car_speed = 0
                
                if count_track < max_count_tracks:
                    poprzednia_ilosc_pointow = ilosc_mid_pointow
                    ilosc_mid_pointow = math.ceil((count_track/max_count_tracks) * max_ilosc_mid_pointow)
                    if ilosc_mid_pointow < poprzednia_ilosc_pointow:
                        ilosc_mid_pointow = poprzednia_ilosc_pointow
                    #
                    generate_track(ilosc_mid_pointow)
                    car_angle = -math.degrees(math.atan2(current_track["lines"][0][3] - current_track["lines"][0][1], current_track["lines"][0][2] - current_track["lines"][0][0]))
                    car_rect.center = (current_track["start_point_x"], current_track["start_point_y"])
                else:
                    gra_uruchomiona = False
                    gra_ukonczona = True
                    timer_main.freeze()
            #        

        # Obliczenia nowej pozycji auta
        car_rect.x += car_speed * pygame.math.Vector2(1, 0).rotate(-car_angle).x
        car_rect.y += car_speed * pygame.math.Vector2(1, 0).rotate(-car_angle).y

        # Sprawdzenie, czy auto nie opuściło obszaru gry
        if car_rect.left < 0:
            car_rect.left = 0
        if car_rect.right > width:
            car_rect.right = width
        if car_rect.top < 0:
            car_rect.top = 0
        if car_rect.bottom > height:
            car_rect.bottom = height
        
        # Wyświetlanie timerów
        draw_text(screen, f"Czas łączny: {convert_timers_to_text(timer_main)}", width/2, 15, 35)
        draw_text(screen, f"Czas toru: {convert_timers_to_text(timer_track)}", width/2, 35, 25)


        # Rysowanie punktów
        # for point in current_track["points"]:
            # pygame.draw.circle(screen, track_color, (int(point[0]), int(point[1])), 2)
        
        # Rysowanie linii toru
        for line in current_track["lines"]:
            pygame.draw.line(screen, track_color, (line[0], line[1]), (line[2], line[3]), 5)
        
        # Rysowanie zaokrągleń toru
        for i in range(0, len(current_track["lines_round"])-2, 2):
            punkt1 = (current_track["lines_round"][i][2], current_track["lines_round"][i][3])
            punkt2 = (current_track["lines_round"][i+2][0], current_track["lines_round"][i+2][1])
            srodek = middle_between_points(punkt1, punkt2)
            # draw_semicircle(screen, srodek, punkt1, punkt2, (255, 0, 0))
            # current_track["test_points"].append(punkt1)
            # current_track["test_points"].append(punkt2)
            # current_track["test_points"].append(srodek)

        # Rysowanie zamknięcia toru
        draw_semicircle(screen, current_track["points"][0], (current_track["lines"][0][0], current_track["lines"][0][1]), (current_track["lines"][1][0], current_track["lines"][1][1]), track_color)
        draw_semicircle(screen, current_track["points"][-1], (current_track["lines"][-1][2], current_track["lines"][-1][3]), (current_track["lines"][-2][2], current_track["lines"][-2][3]), track_color)

        # Kolorowanie toru
        for i in range(0, len(current_track["track_points"])-3, 4):
            polygon = [
                current_track["track_points"][i+0],
                current_track["track_points"][i+2],
                current_track["track_points"][i+3],
                current_track["track_points"][i+1],
            ]
            pygame.draw.polygon(screen, track_inside_color, polygon)
        pygame.draw.circle(screen, track_inside_color, current_track["points"][0], calculate_distance(current_track["points"][0], (current_track["lines"][0][0], current_track["lines"][0][1])))
        pygame.draw.circle(screen, track_inside_color, current_track["points"][-1], calculate_distance(current_track["points"][-1], (current_track["lines"][-1][2], current_track["lines"][-1][3])))

        # Rysowanie lini przerywanej
        for i in range(0, len(current_track["middle_line_points"])-1, 1):
            draw_dashed_line(screen, (250, 245, 240), current_track["middle_line_points"][i], current_track["middle_line_points"][i+1], 10, 20)

        # Rysowanie punktów i linii testowych
        for point in current_track["test_points"]:
            pygame.draw.circle(screen, (255, 0, 0), (int(point[0]), int(point[1])), 5)
        for line in current_track["test_lines"]:
            pygame.draw.line(screen, (0, 0, 255), (line[0], line[1]), (line[2], line[3]), 5)

        # Rysowanie flag
        screen.blit(flag_end_img, flag_end.topleft)

        # Rysowanie auta
        rotated_car = pygame.transform.rotate(car_image, car_angle)
        rotated_rect = rotated_car.get_rect(center=car_rect.center)
        screen.blit(rotated_car, rotated_rect.topleft)

        # Generowanie nowego toru co x sekundy
        # czestotliwosc_generowania = 10 # sekundy
        # last_generowanie = 0
        # aktualna_sekunda = int(pygame.time.get_ticks() / 1000)
        # if aktualna_sekunda % czestotliwosc_generowania == 0 and aktualna_sekunda != last_generowanie:
        #     generate_track(ilosc_mid_pointow)
        #     last_generowanie = aktualna_sekunda

        draw_text(screen, f"Tor #{count_track}/{max_count_tracks}", width - 60, 20)

    # Start gry i odliczanie
    if not gra_uruchomiona and not gra_ukonczona:
        draw_text(screen, "Kliknij SPACE aby rozpocząć grę!", width/2, height/2, 55)

    # Wyświetlanie ekranu końcowego
    if gra_ukonczona:
        draw_text(screen, f"Gratulacje! Ukończyłeś wszystkie tory w {convert_timers_to_text(timer_main)}", width/2, height/2, 40)
        draw_text(screen, f"Kliknij R aby zrestartować grę", width/2, height/2+40, 20)
    
    # Aktualizacja ekranu
    pygame.display.flip()

    # Ustawienie liczby klatek na sekundę
    clock.tick(60)
