
import random
import threading
import time
import json


class Game:
    def __init__(self, config):
        self.rooms = config['rooms']
        self.monster_sleep_time = config['monster_sleep_time']
        self.lives = config['lives']
        self.current_room = 0
        self.monster_awake = False
        self.monster_room = 0
        self.game_log = []
        self.checked_rooms = [False] * self.rooms  # Список для отслеживания проверенных комнат
        self.keys_found = [False] * self.rooms  # Список для отслеживания найденных ключей в комнатах
        self.commode_checked = [False] * self.rooms  # Отслеживание, был ли осмотрен комод
        self.items_checked = [False] * self.rooms  # Отслеживание, были ли осмотрены вещи
        self.has_key = False  # Индикатор наличия ключа
        self.monster_thread = threading.Thread(target=self.monster_activity)
        self.log_thread = threading.Thread(target=self.log_events)

    def monster_activity(self):
        while self.lives > 0:
            time.sleep(self.monster_sleep_time)
            self.monster_awake = True
            self.monster_room = random.randint(0, self.rooms - 1)
            self.log_event("Монстр проснулся и переместился в комнату {}".format(self.monster_room + 1))
            time.sleep(5)  # Монстр бодрствует
            self.monster_awake = False
            self.log_event("Монстр снова заснул!")

    def log_events(self):
        with open('game_log.txt', 'w', encoding='utf-8') as log_file:
            while self.lives > 0:
                for event in self.game_log:
                    log_file.write(event + "\n")
                self.game_log.clear()  # Очищаем логи после записи
                time.sleep(2)

    def log_event(self, event):
        self.game_log.append(f"[{time.strftime('%H:%M:%S')}] {event}")

    def start_game(self):
        print("Добро пожаловать в VirolajnenQuest!")
        self.monster_thread.start()
        self.log_thread.start()
        while self.lives > 0 and self.current_room < self.rooms:
            self.play_room()
        if self.lives <= 0:
            print("Вы погибли! Игра окончена.")
        elif self.current_room >= self.rooms:
            print("Поздравляем, вы прошли квест!")

    def play_room(self):
        print("\nВы находитесь в комнате:", self.current_room + 1)
        if self.monster_awake and self.monster_room == self.current_room:
            print("Осторожно! Монстр поблизости!")
            self.lives -= 1
            self.log_event("Встреча с монстром. Осталось жизней: " + str(self.lives))
            if self.lives <= 0:
                return

        print("Что вы будете делать?")
        print("1 - Обыскать комод")
        print("2 - Осмотреть вещи")
        print("3 - Осмотреть подвал на наличие выхода (если там есть выход, то вы победите)")

        choice = input("Ваш выбор: ")

        if choice == '1':
            self.log_event("Игрок обыскал комод.")
            if not self.commode_checked[self.current_room]:
                found_item = random.choice([None, "ключ", "карта", "ничего"])
                if found_item == "ключ":
                    print("Вы нашли ключ в комоде!")
                    self.has_key = True  # Добавить ключ в инвентарь
                elif found_item:
                    print(f"Вы нашли {found_item} в комоде!")
                else:
                    print("В комоде ничего не оказалось.")
                self.commode_checked[self.current_room] = True
            else:
                print("Вы уже проверяли комод в этой комнате.")

        elif choice == '2':
            self.log_event("Игрок осмотрел вещи.")
            if not self.items_checked[self.current_room]:
                found_item = random.choice([None, "фляга с водой", "еда", "ключ", "ничего"])
                if found_item == "ключ":
                    print("Вы нашли ключ среди вещей!")
                    self.has_key = True  # Добавить ключ в инвентарь
                elif found_item:
                    print(f"Вы нашли {found_item} среди вещей!")
                else:
                    print("Среди вещей ничего интересного.")
                self.items_checked[self.current_room] = True
            else:
                print("Вы уже проверяли вещи в этой комнате.")

        elif choice == '3':
            self.log_event("Игрок осмотрел подвал на наличие выхода.")
            if self.checked_rooms[self.current_room]:
                print("Вы уже осмотрели эту комнату на наличие выхода.")
            else:
                self.checked_rooms[self.current_room] = True
                if random.random() < 0.3:  # 30% шанс найти выход
                    print("Вы нашли выход!")
                    if self.has_key:  # Проверка на наличие ключа
                        print("Вы открываете выход с помощью ключа! Поздравляем!")
                        self.current_room = self.rooms  # Завершаем игру
                        return
                    else:
                        print("У вас нет ключа для открытия выхода. Вам нужно его найти!")
                else:
                    print("Вы не нашли выхода. Переходите в следующую комнату.")

                # Переход в следующую комнату, если выход не найден
                if self.current_room < self.rooms - 1:
                    self.current_room += 1
                    self.log_event("Игрок переместился в комнату {}".format(self.current_room + 1))
        else:
            print("Некорректный выбор, попробуйте снова.")

def load_config():
    try:
        with open('config.json') as config_file:
            config = json.load(config_file)
            return {
                'rooms': config.get('rooms', 10),
                'monster_sleep_time': config.get('monster_sleep_time', 60),
                'lives': config.get('lives', 3)
            }
    except (FileNotFoundError, json.JSONDecodeError):
        return {'rooms': 10, 'monster_sleep_time': 60, 'lives': 3}

if __name__ == "__main__":
    config = load_config()
    game = Game(config)
    game.start_game()
