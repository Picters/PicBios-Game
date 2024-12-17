import pygame
import sys
import pyttsx3
import os
import time
import threading

# Инициализация Pygame
pygame.init()

# Определение цветов
BLUE = (0, 0, 128)
DARK_BLUE = (0, 0, 100)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREY = (200, 200, 200)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Установка полноэкранного режима
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("PicBios")

# Определение шрифтов
title_font = pygame.font.SysFont('Helvetica', 72)
menu_font = pygame.font.SysFont('Helvetica', 48)
info_font = pygame.font.SysFont('Helvetica', 36)

# Функция для рендеринга текста
def render_text(text, font, color):
    return font.render(text, True, color)

# Состояния приложения
STATE_MAIN_MENU = 'main_menu'
STATE_PC_INFO = 'pc_info'
STATE_AI_MENU = 'ai_menu'
STATE_SCANNING = 'scanning'
STATE_VIRUS_REMOVAL = 'virus_removal'
STATE_FINAL_MESSAGE = 'final_message'

class PicBiosApp:
    def __init__(self, screen):
        self.screen = screen
        self.state = STATE_MAIN_MENU
        self.clock = pygame.time.Clock()
        self.menu_items = ["PC Info", "AI"]
        self.current_selection = 0

        # Инициализация TTS
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Скорость речи

        # Загрузка изображения AI
        self.ai_image = None
        self.ai_image_rect = None
        self.load_ai_image()

        # Контроль приветствия
        self.ai_entry_time = None
        self.ai_greeting_played = False
        self.first_ai_entry = True

        # Контроль сканирования и удаления вирусов
        self.scanning = False
        self.removing = False
        self.scan_start_time = None
        self.scan_duration = 10  # Секунды
        self.removal_duration = 10  # Секунды
        self.scan_progress = 0
        self.removal_progress = 0

    def load_ai_image(self):
        try:
            image_path = "./kira.png"
            if not os.path.isfile(image_path):
                print(f"Изображение '{image_path}' не найдено.")
                return

            self.ai_image = pygame.image.load(image_path).convert_alpha()
            
            # Получение размеров экрана и изображения
            screen_width, screen_height = self.screen.get_size()
            img_width, img_height = self.ai_image.get_size()
            
            # Максимальные размеры изображения
            max_width = screen_width // 3
            max_height = screen_height // 3

            # Вычисление коэффициента масштабирования
            scale_factor = min(max_width / img_width, max_height / img_height, 1)

            # Новые размеры изображения
            new_size = (int(img_width * scale_factor), int(img_height * scale_factor))
            self.ai_image = pygame.transform.scale(self.ai_image, new_size)
            self.ai_image_rect = self.ai_image.get_rect(center=(screen_width / 2, screen_height / 2 + 100))
            print(f"Изображение загружено и масштабировано до: {new_size}")
        except Exception as e:
            print(f"Ошибка при загрузке изображения: {e}")
            self.ai_image = None

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)  # Ограничение до 60 FPS

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_app()
            elif event.type == pygame.KEYDOWN:
                if self.state == STATE_MAIN_MENU:
                    if event.key == pygame.K_UP:
                        self.current_selection = (self.current_selection - 1) % len(self.menu_items)
                    elif event.key == pygame.K_DOWN:
                        self.current_selection = (self.current_selection + 1) % len(self.menu_items)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self.select_menu_item()
                    elif event.key == pygame.K_ESCAPE:
                        self.quit_app()
                elif self.state == STATE_PC_INFO:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_MAIN_MENU
                elif self.state == STATE_AI_MENU:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self.start_scanning()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = STATE_MAIN_MENU
                elif self.state in [STATE_SCANNING, STATE_VIRUS_REMOVAL, STATE_FINAL_MESSAGE]:
                    pass  # Игнорировать все клавиши во время сканирования и удаления
            elif event.type == pygame.USEREVENT + 1:
                if self.state == STATE_SCANNING:
                    self.state = STATE_VIRUS_REMOVAL
                    self.start_removal()
                elif self.state == STATE_VIRUS_REMOVAL:
                    self.state = STATE_FINAL_MESSAGE
                    self.start_final_message()

    def select_menu_item(self):
        selected_item = self.menu_items[self.current_selection]
        if selected_item == "PC Info":
            self.state = STATE_PC_INFO
        elif selected_item == "AI":
            self.state = STATE_AI_MENU
            if self.first_ai_entry:
                self.ai_entry_time = time.time()
                self.first_ai_entry = False

    def start_scanning(self):
        if not self.scanning:
            self.state = STATE_SCANNING
            self.scan_start_time = time.time()
            self.scan_progress = 0
            self.scanning = True
            threading.Thread(target=self.say_scan_greeting).start()

    def start_removal(self):
        if not self.removing:
            self.state = STATE_VIRUS_REMOVAL
            self.removal_start_time = time.time()
            self.removal_progress = 0
            self.removing = True
            threading.Thread(target=self.say_removal_greeting).start()

    def start_final_message(self):
        threading.Thread(target=self.say_final_message).start()
        pygame.time.set_timer(pygame.USEREVENT + 2, 3000)  # Завершить через 3 секунды

    def say_ai_greeting(self):
        greeting_text = "Привет. Давай дружить, дружище? Я починю твой компьютер, друг!"
        try:
            self.tts_engine.say(greeting_text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Ошибка TTS: {e}")

    def say_scan_greeting(self):
        greeting_text = "Начинаю сканирование твоего ПК, дружище!"
        try:
            self.tts_engine.say(greeting_text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Ошибка TTS: {e}")

    def say_removal_greeting(self):
        greeting_text = "Обнаружены вирусы. Устраняю проблему..."
        try:
            self.tts_engine.say(greeting_text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Ошибка TTS: {e}")

    def say_final_message(self):
        final_text = "Ну что. Как дела? Как жизнь?"
        try:
            self.tts_engine.say(final_text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Ошибка TTS: {e}")

    def update(self):
        if self.state == STATE_SCANNING:
            elapsed_time = time.time() - self.scan_start_time
            self.scan_progress = min(int((elapsed_time / self.scan_duration) * 100), 100)
            if self.scan_progress >= 100:
                pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # Переход к удалению через 1 секунду
        elif self.state == STATE_VIRUS_REMOVAL:
            elapsed_time = time.time() - self.removal_start_time
            self.removal_progress = min(int((elapsed_time / self.removal_duration) * 100), 100)
            if self.removal_progress >= 100:
                pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # Переход к финальному сообщению через 1 секунду

    def render(self):
        self.screen.fill(BLUE)
        if self.state == STATE_MAIN_MENU:
            self.render_main_menu()
        elif self.state == STATE_PC_INFO:
            self.render_pc_info()
        elif self.state == STATE_AI_MENU:
            self.render_ai_menu()
            self.handle_ai_greeting()
        elif self.state == STATE_SCANNING:
            self.render_scanning()
        elif self.state == STATE_VIRUS_REMOVAL:
            self.render_removal()
        elif self.state == STATE_FINAL_MESSAGE:
            self.render_final_message()

    def handle_ai_greeting(self):
        if self.ai_entry_time and not self.ai_greeting_played:
            current_time = time.time()
            if current_time - self.ai_entry_time >= 1:
                self.say_ai_greeting()
                self.ai_greeting_played = True

    def render_main_menu(self):
        # Заголовок
        title_text = render_text("PicBios", title_font, WHITE)
        title_rect = title_text.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 4))
        self.screen.blit(title_text, title_rect)

        # Пункты меню
        for index, item in enumerate(self.menu_items):
            if index == self.current_selection:
                color = YELLOW
                bg_color = DARK_BLUE
            else:
                color = WHITE
                bg_color = BLUE
            menu_text = render_text(item, menu_font, color)
            menu_surface = pygame.Surface((menu_text.get_width() + 40, menu_text.get_height() + 20))
            menu_surface.fill(bg_color)
            menu_surface.blit(menu_text, (20, 10))
            menu_rect = menu_surface.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2 + index * 60))
            self.screen.blit(menu_surface, menu_rect)

    def render_pc_info(self):
        # Заголовок
        info_title = render_text("PC Info", title_font, WHITE)
        info_title_rect = info_title.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 4))
        self.screen.blit(info_title, info_title_rect)

        # Информация
        info_text_lines = [
            "This is an ancient PC developed by PicLab in 1998.",
            "",
            "Specifications:",
            "- Processor: Intel Pentium II",
            "- RAM: 256MB",
            "- Storage: 40GB HDD",
            "- Graphics: NVIDIA RIVA TNT2",
            "",
            "Press ESC to return to the main menu."
        ]
        for i, line in enumerate(info_text_lines):
            info_text = render_text(line, info_font, WHITE)
            info_rect = info_text.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 3 + i * 40))
            self.screen.blit(info_text, info_rect)

    def render_ai_menu(self):
        # Заголовок
        ai_title = render_text("AI", title_font, WHITE)
        ai_title_rect = ai_title.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 6))
        self.screen.blit(ai_title, ai_title_rect)

        # Изображение
        if self.ai_image and self.ai_image_rect:
            self.screen.blit(self.ai_image, self.ai_image_rect)
        else:
            error_text = render_text("Image 'kira.png' not found.", info_font, WHITE)
            error_rect = error_text.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2))
            self.screen.blit(error_text, error_rect)

        # Описание
        description_lines = [
            "Это искусственный интеллект, разработанный компанией PicLab.",
            "Он поможет вам починить ваш компьютер и сделать его быстрее."
        ]
        for i, line in enumerate(description_lines):
            desc_text = render_text(line, info_font, WHITE)
            desc_rect = desc_text.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2 + i * 40 + 100))
            self.screen.blit(desc_text, desc_rect)

        # Кнопка "Сканировать"
        scan_text = render_text("Сканировать", menu_font, YELLOW)
        scan_surface = pygame.Surface((scan_text.get_width() + 40, scan_text.get_height() + 20))
        scan_surface.fill(DARK_BLUE)
        scan_surface.blit(scan_text, (20, 10))
        self.scan_button_rect = scan_surface.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2 + 200))
        self.screen.blit(scan_surface, self.scan_button_rect)

    def render_scanning(self):
        # Заголовок
        ai_title = render_text("AI", title_font, WHITE)
        ai_title_rect = ai_title.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 6))
        self.screen.blit(ai_title, ai_title_rect)

        # Приветственное сообщение
        scanning_message = render_text("Начинаю сканирование твоего ПК, дружище!", info_font, WHITE)
        scanning_message_rect = scanning_message.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2 - 50))
        self.screen.blit(scanning_message, scanning_message_rect)

        # Изображение под прогресс-баром
        if self.ai_image and self.ai_image_rect:
            self.screen.blit(self.ai_image, self.ai_image_rect)

        # Прогресс-бар
        progress_width = self.screen.get_width() // 2
        progress_height = 30
        progress_x = (self.screen.get_width() - progress_width) // 2
        progress_y = self.screen.get_height() / 2

        # Фон прогресс-бара
        pygame.draw.rect(self.screen, GREY, (progress_x, progress_y, progress_width, progress_height))
        # Заполненная часть прогресс-бара
        pygame.draw.rect(self.screen, GREEN, (progress_x, progress_y, progress_width * (self.scan_progress / 100), progress_height))
        # Рамка прогресс-бара
        pygame.draw.rect(self.screen, WHITE, (progress_x, progress_y, progress_width, progress_height), 2)

        # Текст процента
        percent_text = render_text(f"{self.scan_progress}%", info_font, WHITE)
        percent_rect = percent_text.get_rect(center=(self.screen.get_width() / 2, progress_y + progress_height + 20))
        self.screen.blit(percent_text, percent_rect)

    def render_removal(self):
        # Заголовок
        ai_title = render_text("AI", title_font, WHITE)
        ai_title_rect = ai_title.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 6))
        self.screen.blit(ai_title, ai_title_rect)

        # Приветственное сообщение
        removal_message = render_text("Обнаружены вирусы. Устраняю проблему...", info_font, WHITE)
        removal_message_rect = removal_message.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2 - 50))
        self.screen.blit(removal_message, removal_message_rect)

        # Изображение под прогресс-баром
        if self.ai_image and self.ai_image_rect:
            self.screen.blit(self.ai_image, self.ai_image_rect)

        # Прогресс-бар
        progress_width = self.screen.get_width() // 2
        progress_height = 30
        progress_x = (self.screen.get_width() - progress_width) // 2
        progress_y = self.screen.get_height() / 2

        # Фон прогресс-бара
        pygame.draw.rect(self.screen, GREY, (progress_x, progress_y, progress_width, progress_height))
        # Заполненная часть прогресс-бара
        pygame.draw.rect(self.screen, GREEN, (progress_x, progress_y, progress_width * (self.removal_progress / 100), progress_height))
        # Рамка прогресс-бара
        pygame.draw.rect(self.screen, WHITE, (progress_x, progress_y, progress_width, progress_height), 2)

        # Текст процента
        percent_text = render_text(f"{self.removal_progress}%", info_font, WHITE)
        percent_rect = percent_text.get_rect(center=(self.screen.get_width() / 2, progress_y + progress_height + 20))
        self.screen.blit(percent_text, percent_rect)

    def render_final_message(self):
        # Темно-синий фон
        self.screen.fill(DARK_BLUE)

        # Изображение в центре
        if self.ai_image and self.ai_image_rect:
            center_rect = self.ai_image.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2))
            self.screen.blit(self.ai_image, center_rect)

    def quit_app(self):
        self.tts_engine.stop()
        pygame.quit()
        sys.exit()

def main():
    app = PicBiosApp(screen)
    app.run()

if __name__ == "__main__":
    main()
