import pygame


class InputManager:
    """
    Standard controller button mapping assumed (Xbox-style layout):
        Button 0 -> A (ACCEPT)
        Button 1 -> B (BACK)
        Button 3 -> Y (DETAIL)
        Button 4 -> LB (TAB_LEFT)
        Button 5 -> RB (TAB_RIGHT)

    Keyboard equivalents:
        Enter/Space -> ACCEPT
        Escape      -> BACK
        Y           -> DETAIL
        Q           -> TAB_LEFT
        E           -> TAB_RIGHT
    """

    def __init__(self, joysticks):
        self.actions = {
            "UP": False,
            "DOWN": False,
            "LEFT": False,
            "RIGHT": False,
            "ACCEPT": False,
            "BACK": False,
            "DETAIL": False,
            "TAB_LEFT": False,
            "TAB_RIGHT": False,
            "SCROLL": 0,
            "MOUSE_POS": (0, 0),
            "CLICK": False,
            "ANY_KEY": None,
        }
        self.joy_delay = 0
        self.joysticks = joysticks
        self.last_input = "mouse"

    def reset_frame(self):
        for k in [
            "UP",
            "DOWN",
            "LEFT",
            "RIGHT",
            "ACCEPT",
            "BACK",
            "DETAIL",
            "TAB_LEFT",
            "TAB_RIGHT",
            "CLICK",
        ]:
            self.actions[k] = False
        self.actions["SCROLL"] = 0
        self.actions["ANY_KEY"] = None

    def process_events(self, W, H):
        self.reset_frame()
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.VIDEORESIZE:
                global screen
                screen = pygame.display.set_mode((event.w, event.h), pygame.SCALED)

            # KEYBOARD
            if event.type == pygame.KEYDOWN:
                self.last_input = "keyboard"

                self.actions["ANY_KEY"] = event
                if event.key == pygame.K_UP:
                    self.actions["UP"] = True
                if event.key == pygame.K_DOWN:
                    self.actions["DOWN"] = True
                if event.key == pygame.K_LEFT:
                    self.actions["LEFT"] = True
                if event.key == pygame.K_RIGHT:
                    self.actions["RIGHT"] = True
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.actions["ACCEPT"] = True
                if event.key == pygame.K_ESCAPE:
                    self.actions["BACK"] = True
                if event.key == pygame.K_y:
                    self.actions["DETAIL"] = True
                if event.key == pygame.K_q:
                    self.actions["TAB_LEFT"] = True
                if event.key == pygame.K_e:
                    self.actions["TAB_RIGHT"] = True

            # MOUSE / TOUCH
            if event.type == pygame.MOUSEMOTION:
                self.last_input = "mouse"
                self.actions["MOUSE_POS"] = event.pos
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.last_input = "mouse"
                self.actions["CLICK"] = True
                self.actions["MOUSE_POS"] = event.pos
                if event.button == 1:
                    self.actions["ACCEPT"] = True
            if event.type == pygame.MOUSEWHEEL:
                self.last_input = "mouse"
                self.actions["SCROLL"] = event.y

            if event.type == pygame.FINGERDOWN:
                self.last_input = "touch"
                self.actions["CLICK"] = True
                self.actions["ACCEPT"] = True
                self.actions["MOUSE_POS"] = (int(event.x * W), int(event.y * H))
            if event.type == pygame.FINGERMOTION:
                self.last_input = "touch"
                self.actions["MOUSE_POS"] = (int(event.x * W), int(event.y * H))

            # CONTROLLER
            if event.type == pygame.JOYBUTTONDOWN:
                self.last_input = "controller"
                if event.button == 0:
                    self.actions["ACCEPT"] = True
                if event.button == 1:
                    self.actions["BACK"] = True
                if event.button == 3:
                    self.actions["DETAIL"] = True
                if event.button == 4:
                    self.actions["TAB_LEFT"] = True
                if event.button == 5:
                    self.actions["TAB_RIGHT"] = True

            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                self.joysticks[joy.get_instance_id()] = joy
            if event.type == pygame.JOYDEVICEREMOVED:
                if event.instance_id in self.joysticks:
                    del self.joysticks[event.instance_id]

        # Controller D-Pad/Axis Debouncing
        if self.joysticks and current_time > self.joy_delay:
            moved = False
            for joy in self.joysticks.values():
                ax_x, ax_y = joy.get_axis(0), joy.get_axis(1)
                hat_x, hat_y = joy.get_hat(0) if joy.get_numhats() > 0 else (0, 0)
                if ax_y < -0.5 or hat_y > 0.5:
                    self.actions["UP"] = True
                    moved = True
                elif ax_y > 0.5 or hat_y < -0.5:
                    self.actions["DOWN"] = True
                    moved = True
                elif ax_x < -0.5 or hat_x < -0.5:
                    self.actions["LEFT"] = True
                    moved = True
                elif ax_x > 0.5 or hat_x > 0.5:
                    self.actions["RIGHT"] = True
                    moved = True
            if moved:
                self.last_input = "controller"
                self.joy_delay = current_time + 200

        if self.last_input == "mouse":
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)

        return None
