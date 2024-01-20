import unittest
import importlib
from pathlib import Path
import json
import os
from datetime import datetime
from main import format_time, calculate_distance, middle_between_points, czy_linie_sie_przecinaja, znajdz_punkt_przeciecia

class TestCarGame(unittest.TestCase):

    def test_required_packages_installed(self):
        required_packages = ["pygame", "sys", "os", "random", "math", "numpy", "time", "json", "datetime"]
        for package in required_packages:
            with self.subTest(package=package):
                try:
                    importlib.import_module(package)
                except ImportError:
                    self.fail(f"Paczka {package} nie jest zainstalowana. Wpisz komendę instalacyjną: pip install {package}")

    def test_required_files_exist(self):
        required_files = [
            "main.py", 
            "images/background/background_0.png", 
            "images/car/car.png", 
            "images/flags/flag_end_0.png", "images/flags/flag_end_1.png",
            "images/lights/light_0.png", "images/lights/light_1.png", 
            "images/car/logo.png", 
            "images/lights/traffic_lights_0.png",  "images/lights/traffic_lights_1.png", "images/lights/traffic_lights_2.png", 
        ]
        for file in required_files:
            with self.subTest(file=file):
                self.assertTrue(Path(file).is_file(), f"Brakujący plik: {file}")

    def test_game_no_errors(self):
        try:
            import main
            importlib.reload(main)
            main.main(True)

        except SystemExit:
            pass

        except Exception as e:
            self.fail(f"Error: {e}")

    def test_edit_and_save_records_file(self):
        # Przygotowanie danych testowych
        test_file_path = 'records_test.json'
        current_date = datetime.now().strftime("%d.%m.%Y")
        new_record_value = 10000

        # Odczytanie pliku
        try:
            with open(test_file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"records": {}}

        # Edycja danych
        data["records"][current_date] = new_record_value

        # Zapisanie pliku
        with open(test_file_path, 'w') as file:
            json.dump(data, file)

        # Odczytanie pliku po edycji
        with open(test_file_path, 'r') as file:
            data_after_edit = json.load(file)

        # Sprawdzenie, czy edycja została poprawnie zapisana
        self.assertEqual(data_after_edit["records"][current_date], new_record_value, "Błąd edycji pliku od zapisywania rekordów")

        # Usunięcie pliku testowego po zakończeniu testu
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

    def test_function_format_time(self):
        result = format_time(12456)
        expected_result = "12.5s"

        self.assertEqual(result, expected_result, "Funkcja nie zwróciła oczekiwanego wyniku")
    
    def test_function_calculate_distance(self):
        result = calculate_distance((12, 34), (56, 78))
        expected_result = 62.22539674441618

        self.assertEqual(result, expected_result, "Funkcja nie zwróciła oczekiwanego wyniku")
    
    def test_function_middle_between_points(self):
        result = middle_between_points((12, 34), (56, 78))
        expected_result = (34, 56)

        self.assertEqual(result, expected_result, "Funkcja nie zwróciła oczekiwanego wyniku")

    def test_function_czy_linie_sie_przecinaja(self):
        result_0 = czy_linie_sie_przecinaja((12, 34, 56, 78), (90, 12, 34, 56))
        expected_result_0 = True
        result_1 = czy_linie_sie_przecinaja((10, 20, 40, 20), (10, 30, 40, 30))
        expected_result_1 = False

        self.assertEqual(result_0, expected_result_0, "Funkcja nie zwróciła oczekiwanego wyniku")
        self.assertEqual(result_1, expected_result_1, "Funkcja nie zwróciła oczekiwanego wyniku")

    def test_function_znajdz_punkt_przeciecia(self):
        result_0 = znajdz_punkt_przeciecia((12, 34, 56, 78), (90, 12, 34, 56))
        expected_result_0 = (34.0, 56.0)
        result_1 = znajdz_punkt_przeciecia((10, 20, 40, 20), (10, 30, 40, 30))
        expected_result_1 = None

        self.assertEqual(result_0, expected_result_0, "Funkcja nie zwróciła oczekiwanego wyniku")
        self.assertEqual(result_1, expected_result_1, "Funkcja nie zwróciła oczekiwanego wyniku")


if __name__ == '__main__':
    unittest.main()
