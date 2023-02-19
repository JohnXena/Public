from pygame import draw, Rect, mouse
class Button():
    def __init__(self, font, text, text_colour, width, height, pos, elevation, top, bottom, change, border):
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elevation = elevation
        self.original_y_pos = pos[1]

        # top rectangle
        self.top_rect = Rect(pos, (width, height))
        self.original_top_colour = top
        self.dynamic_top_colour = self.original_top_colour
        self.border_radius = border
        self.change_colour = change

        # drop shadow
        self.bottom_rect = Rect(pos, (width, elevation))
        self.bottom_colour = bottom

        # text
        self.text_surf = font.render(text, True, text_colour)
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

    def draw(self, screen):
        self.check_click()

        # elevation logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elevation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elevation

        draw.rect(screen, self.bottom_colour, self.bottom_rect, border_radius = self.border_radius)
        draw.rect(screen, self.top_colour, self.top_rect, border_radius = self.border_radius)
        screen.blit(self.text_surf, self.text_rect)

    def check_click(self):
        mouse_pos = mouse.get_pos()
        # if mouse on button
        if self.top_rect.collidepoint(mouse_pos):
            self.top_colour = self.change_colour
            # if left clicked
            if mouse.get_pressed()[0]:
                self.dynamic_elevation = 0
                self.pressed = True
                return True
            else:
                self.dynamic_elevation = self.elevation
                if self.pressed:
                    self.pressed = False
        else:
            self.top_colour = self.original_top_colour
            self.dynamic_elevation = self.elevation
        return False
