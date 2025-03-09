import pygame


class Button:
    def __init__(
        self,
        position: tuple[int, int],
        size: tuple[int, int],
        color: pygame.Color,
        color_bg: pygame.Color,
        color_font: pygame.Color,
        callback=None,
        text="",
        font="Segoe Print",
        font_size=16,
    ):
        self.color = color
        self.size = size
        self.callback = callback
        self.surf = pygame.Surface(size)
        self.rect = self.surf.get_rect(center=position)
        self.color_bg = color_bg

        if len(color) == 4:
            self.surf.set_alpha(color[3])

        self.font = pygame.font.SysFont(font, font_size)
        self.txt = text
        self.font_color = color_font
        self.txt_surf = self.font.render(self.txt, 1, self.font_color)
        self.txt_rect = self.txt_surf.get_rect(center=[wh // 2 for wh in self.size])

    def draw(self, screen):
        self.mouseover()

        self.surf.fill(self.curcolor)
        self.surf.blit(self.txt_surf, self.txt_rect)
        screen.blit(self.surf, self.rect)

    def mouseover(self):
        self.curcolor = self.color
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.curcolor = self.color_bg

    def call_back(self, *args):
        if self.callback:
            return self.callback(*args)


class text:
    def __init__(
        self,
        text,
        position,
        color=[100, 100, 100],
        font="Segoe Print",
        font_size=15,
        mid=False,
    ):
        self.position = position
        self.font = pygame.font.SysFont(font, font_size)
        self.text_surf = self.font.render(text, 1, color)

        if len(color) == 4:
            self.text_surf.set_alpha(color[3])

        if mid:
            self.position = self.text_surf.get_rect(center=position)

    def draw(self, screen):
        screen.blit(self.text_surf, self.position)
