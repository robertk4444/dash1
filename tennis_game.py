#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RETRO TENNIS GAME (PONG)
Klasyczna gra w tenisa jak na starych telewizorach!

Sterowanie:
- Gracz 1 (lewa paletka): W (góra), S (dół)
- Gracz 2 (prawa paletka): Strzałka w górę, Strzałka w dół
- ESC - wyjście z gry
- SPACJA - restart po zakończeniu gry

Gra do 10 punktów!
"""

import pygame
import sys
import random

# Inicjalizacja pygame
pygame.init()

# Stałe gry
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Kolory (retro - czarno-białe)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# Ustawienia paletki
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
PADDLE_SPEED = 7

# Ustawienia piłki
BALL_SIZE = 15
BALL_SPEED_X = 5
BALL_SPEED_Y = 5

# Punkty do wygranej
WINNING_SCORE = 10


class Paddle:
    """Klasa reprezentująca paletkę gracza"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def move_up(self):
        """Ruch paletki w górę"""
        if self.y > 0:
            self.y -= self.speed
            self.rect.y = self.y

    def move_down(self):
        """Ruch paletki w dół"""
        if self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
            self.rect.y = self.y

    def draw(self, screen):
        """Rysowanie paletki"""
        pygame.draw.rect(screen, WHITE, self.rect)


class Ball:
    """Klasa reprezentująca piłkę"""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset piłki do środka ekranu"""
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.size = BALL_SIZE
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

        # Losowy kierunek startowy
        direction = random.choice([-1, 1])
        self.speed_x = BALL_SPEED_X * direction
        self.speed_y = BALL_SPEED_Y * random.choice([-1, 1])

    def move(self):
        """Ruch piłki"""
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.x = self.x
        self.rect.y = self.y

        # Odbicie od górnej i dolnej krawędzi
        if self.y <= 0 or self.y >= SCREEN_HEIGHT - self.size:
            self.speed_y *= -1

    def draw(self, screen):
        """Rysowanie piłki"""
        pygame.draw.rect(screen, WHITE, self.rect)


class Game:
    """Główna klasa gry"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RETRO TENNIS - PONG")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)

        # Inicjalizacja obiektów gry
        self.paddle1 = Paddle(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.paddle2 = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball()

        # Wyniki
        self.score1 = 0
        self.score2 = 0
        self.game_over = False
        self.winner = None

    def handle_events(self):
        """Obsługa zdarzeń"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()
        return True

    def handle_input(self):
        """Obsługa sterowania"""
        if not self.game_over:
            keys = pygame.key.get_pressed()

            # Gracz 1 (lewa paletka)
            if keys[pygame.K_w]:
                self.paddle1.move_up()
            if keys[pygame.K_s]:
                self.paddle1.move_down()

            # Gracz 2 (prawa paletka)
            if keys[pygame.K_UP]:
                self.paddle2.move_up()
            if keys[pygame.K_DOWN]:
                self.paddle2.move_down()

    def update(self):
        """Aktualizacja stanu gry"""
        if not self.game_over:
            self.ball.move()

            # Kolizja z paletkami
            if self.ball.rect.colliderect(self.paddle1.rect):
                if self.ball.speed_x < 0:
                    self.ball.speed_x *= -1.05  # Zwiększenie prędkości
                    # Dodanie efektu kąta odbicia
                    paddle_center = self.paddle1.y + PADDLE_HEIGHT // 2
                    ball_center = self.ball.y + BALL_SIZE // 2
                    offset = (ball_center - paddle_center) / (PADDLE_HEIGHT // 2)
                    self.ball.speed_y = offset * 8

            if self.ball.rect.colliderect(self.paddle2.rect):
                if self.ball.speed_x > 0:
                    self.ball.speed_x *= -1.05  # Zwiększenie prędkości
                    # Dodanie efektu kąta odbicia
                    paddle_center = self.paddle2.y + PADDLE_HEIGHT // 2
                    ball_center = self.ball.y + BALL_SIZE // 2
                    offset = (ball_center - paddle_center) / (PADDLE_HEIGHT // 2)
                    self.ball.speed_y = offset * 8

            # Sprawdzenie punktów
            if self.ball.x <= 0:
                self.score2 += 1
                self.check_winner()
                if not self.game_over:
                    self.ball.reset()

            if self.ball.x >= SCREEN_WIDTH:
                self.score1 += 1
                self.check_winner()
                if not self.game_over:
                    self.ball.reset()

    def check_winner(self):
        """Sprawdzenie czy jest zwycięzca"""
        if self.score1 >= WINNING_SCORE:
            self.game_over = True
            self.winner = "GRACZ 1"
        elif self.score2 >= WINNING_SCORE:
            self.game_over = True
            self.winner = "GRACZ 2"

    def reset_game(self):
        """Reset gry"""
        self.score1 = 0
        self.score2 = 0
        self.game_over = False
        self.winner = None
        self.ball.reset()
        self.paddle1.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.paddle2.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.paddle1.rect.y = self.paddle1.y
        self.paddle2.rect.y = self.paddle2.y

    def draw(self):
        """Rysowanie wszystkich elementów gry"""
        # Tło
        self.screen.fill(BLACK)

        # Linia środkowa (przerywana)
        for y in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.rect(self.screen, GRAY, (SCREEN_WIDTH // 2 - 2, y, 4, 10))

        # Paletki i piłka
        self.paddle1.draw(self.screen)
        self.paddle2.draw(self.screen)
        self.ball.draw(self.screen)

        # Wyniki
        score1_text = self.font_large.render(str(self.score1), True, WHITE)
        score2_text = self.font_large.render(str(self.score2), True, WHITE)
        self.screen.blit(score1_text, (SCREEN_WIDTH // 4, 30))
        self.screen.blit(score2_text, (3 * SCREEN_WIDTH // 4 - score2_text.get_width(), 30))

        # Ekran końcowy
        if self.game_over:
            # Półprzezroczyste tło
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            # Komunikaty
            winner_text = self.font_large.render(f"{self.winner} WYGRYWA!", True, WHITE)
            restart_text = self.font_small.render("Naciśnij SPACJĘ aby zagrać ponownie", True, WHITE)
            quit_text = self.font_small.render("ESC - wyjście", True, WHITE)

            self.screen.blit(winner_text,
                           (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
            self.screen.blit(restart_text,
                           (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(quit_text,
                           (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

        # Instrukcje sterowania (podczas gry)
        if not self.game_over:
            control1 = self.font_small.render("W/S", True, GRAY)
            control2 = self.font_small.render("↑/↓", True, GRAY)
            self.screen.blit(control1, (10, SCREEN_HEIGHT - 40))
            self.screen.blit(control2, (SCREEN_WIDTH - 60, SCREEN_HEIGHT - 40))

        pygame.display.flip()

    def run(self):
        """Główna pętla gry"""
        running = True

        # Ekran powitalny
        self.show_welcome_screen()

        while running:
            running = self.handle_events()
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def show_welcome_screen(self):
        """Ekran powitalny"""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            self.screen.fill(BLACK)

            # Tytuł
            title = self.font_large.render("RETRO TENNIS", True, WHITE)
            subtitle = self.font_medium.render("PONG", True, GRAY)

            # Instrukcje
            inst1 = self.font_small.render("GRACZ 1: W (góra) / S (dół)", True, WHITE)
            inst2 = self.font_small.render("GRACZ 2: ↑ (góra) / ↓ (dół)", True, WHITE)
            inst3 = self.font_small.render(f"Graj do {WINNING_SCORE} punktów!", True, GRAY)
            start = self.font_medium.render("Naciśnij SPACJĘ aby rozpocząć", True, WHITE)

            # Pozycjonowanie
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
            self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 160))
            self.screen.blit(inst1, (SCREEN_WIDTH // 2 - inst1.get_width() // 2, 280))
            self.screen.blit(inst2, (SCREEN_WIDTH // 2 - inst2.get_width() // 2, 330))
            self.screen.blit(inst3, (SCREEN_WIDTH // 2 - inst3.get_width() // 2, 380))
            self.screen.blit(start, (SCREEN_WIDTH // 2 - start.get_width() // 2, 480))

            pygame.display.flip()


def main():
    """Funkcja główna"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
