import pygame
import sys
import os
import random
import math

# Ustawienie seed dla random do testów
# random.seed(9999421)

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna gry
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("2D Car Game")

# Wczytanie obrazu auta
car_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "car.png"))
car_rect = car_image.get_rect()
car_rect.center = (width // 2, height // 2)

# Ustawienia auta
car_speed = 0  # Początkowa prędkość
car_max_speed = 5  # Maksymalna prędkość
car_acceleration = 0.1  # Współczynnik przyspieszenia
car_angle = 90

# Ustawienia wyglądu
track_color = (0, 0, 0)
track_width = 75
map_color = (255, 255, 255)
map_margin = 75

# Flaga, czy gra jest uruchomiona
gra_uruchomiona = True

# Główna pętla gry
clock = pygame.time.Clock()


# Funkcja tworząca randomowy tor
current_track = {
    "start_point_x": map_margin,
    "start_point_y": 0,
    "mid_points": [],
    "end_point_x": width - map_margin,
    "end_point_y": 0,
    "points": [],
    "test_points": [],
    "lines": []
}

# Funkcja obliczająca odległość między punktami
def calculate_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
# Funkcja do rysowania półkola
def draw_semicircle(surface, center, point1, point2, color):
    radius = calculate_distance(center, point1)

    # Obliczenia kątów (w radianach) na podstawie punktów
    angle1 = pygame.math.Vector2(point1[0] - center[0], point1[1] - center[1]).angle_to(pygame.math.Vector2(1, 0))
    angle2 = pygame.math.Vector2(point2[0] - center[0], point2[1] - center[1]).angle_to(pygame.math.Vector2(1, 0))
    
    # Zamiana miejscami wartości kątów
    angle1, angle2 = angle2, angle1

    # Rysowanie półkola
    pygame.draw.arc(surface, color, (center[0] - radius, center[1] - radius, 2 * radius+2, 2 * radius+2), angle1/57, angle2/57, 2)
# Funkcja od generowania toru
def generate_track(number_of_mid_points=1):
    global current_track, track_width
    global width, height, map_margin
    global car_rect, car_angle, car_speed

    # Resetowanie ustawień
    current_track["test_points"] = []
    current_track["mid_points"] = []
    current_track["lines"] = []
    current_track["points"] = []

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

    # Funkcja obliczająca środek między dwoma punktami
    def middle_between_points(punkt1, punkt2):
        srodek_x = (punkt1[0] + punkt2[0]) / 2
        srodek_y = (punkt1[1] + punkt2[1]) / 2
        return (int(srodek_x), int(srodek_y))
    # Funkcja sprawdzająca czy dwie linie się przecinają
    def czy_linie_sie_przecinaja(linia1, linia2):
        x1, y1, x2, y2 = linia1
        x3, y3, x4, y4 = linia2

        # Sprawdzenie warunku przecięcia linii
        if (
            (min(x1, x2) <= x3 <= max(x1, x2) and min(y1, y2) <= y3 <= max(y1, y2)) or
            (min(x1, x2) <= x4 <= max(x1, x2) and min(y1, y2) <= y4 <= max(y1, y2)) or
            (min(x3, x4) <= x1 <= max(x3, x4) and min(y3, y4) <= y1 <= max(y3, y4)) or
            (min(x3, x4) <= x2 <= max(x3, x4) and min(y3, y4) <= y2 <= max(y3, y4))
        ):
            return True
        else:
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

    # Ustawianie autka na pozycji startu
    car_angle = -math.degrees(math.atan2(current_track["lines"][0][3] - current_track["lines"][0][1], current_track["lines"][0][2] - current_track["lines"][0][0]))
    car_point = (current_track["start_point_x"], current_track["start_point_y"])
    car_rect.center = car_point
    car_speed = 0
    #

# Generowanie nowego toru co x sekundy
czestotliwosc_generowania = 1 # sekundy
last_generowanie = 0
ilosc_mid_pointow = 3

# Wywołanie funkcji
generate_track(ilosc_mid_pointow)


# Główna pętla gry
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Obsługa naciśnięcia klawisza
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    # Ruch auta tylko jeśli gra jest uruchomiona
    if gra_uruchomiona:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and car_speed > 0:
            car_angle += 5
        if keys[pygame.K_RIGHT] and car_speed > 0:
            car_angle -= 5
        if keys[pygame.K_UP]:
            # Przyspieszenie auta
            car_speed = min(car_speed + car_acceleration, car_max_speed)
        else:
            # Hamowanie auta
            car_speed = max(0, car_speed - car_acceleration)

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

    # Wypełnienie ekranu kolorem tła
    screen.fill(map_color)

    # Rysowanie punktów
    for point in current_track["points"]:
        pygame.draw.circle(screen, track_color, (int(point[0]), int(point[1])), 2)
    
    # Rysowanie punktów testowych
    for point in current_track["test_points"]:
        pygame.draw.circle(screen, (255, 0, 0), (int(point[0]), int(point[1])), 5)
    
    # Rysowanie linii
    for line in current_track["lines"]:
        pygame.draw.line(screen, track_color, (line[0], line[1]), (line[2], line[3]), 3)

    # Rysowanie zamknięcia toru
    draw_semicircle(screen, current_track["points"][0], (current_track["lines"][0][0], current_track["lines"][0][1]), (current_track["lines"][1][0], current_track["lines"][1][1]), track_color)
    draw_semicircle(screen, current_track["points"][-1], (current_track["lines"][-1][2], current_track["lines"][-1][3]), (current_track["lines"][-2][2], current_track["lines"][-2][3]), track_color)

    # Rysowanie auta
    rotated_car = pygame.transform.rotate(car_image, car_angle)
    rotated_rect = rotated_car.get_rect(center=car_rect.center)
    screen.blit(rotated_car, rotated_rect.topleft)

    # Generowanie nowego toru co x sekundy
    aktualna_sekunda = int(pygame.time.get_ticks() / 1000)
    if aktualna_sekunda % czestotliwosc_generowania == 0 and aktualna_sekunda != last_generowanie:
        generate_track(ilosc_mid_pointow)
        last_generowanie = aktualna_sekunda

    # Aktualizacja ekranu
    pygame.display.flip()

    # Ustawienie liczby klatek na sekundę
    clock.tick(60)
