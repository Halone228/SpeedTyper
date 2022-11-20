import random
import shutil
from colorama import Cursor, Back, Style, Fore, ansi, init
from pynput.keyboard import Controller, Key, Listener, KeyCode

init(autoreset=True)

keyboard = Controller()


class Typer:
    position: int
    type_string: str
    TYPING_FORM = 1
    LETTER_FORM = 3
    INFO_FORM = 10
    info_text: str = ''
    stroke: int = 0
    ERROR_FORM = 2
    _params: list
    end_typing: bool

    def clear_line(self):
        ansi.clear_line(2)
        print(' '*self.width, end='\r')

    def clear_screen(self):
        ansi.clear_screen(2)
        for i in range(self.height):
            print(Cursor.POS(1, i), end='')
            self.clear_line()

    def print_info(self):
        self.set_pos(1, self.INFO_FORM)
        self.clear_line()
        print(self.info_text, end='')

    def print_formatted(self):
        self.set_pos(1, self.TYPING_FORM)
        self.clear_line()
        print_text = self.make_string()
        print(print_text, end='')

    def print_letter(self):
        self.set_pos(1, self.LETTER_FORM)
        self.clear_line()
        try:
            key = self.type_string[self.position+1]
        except:
            key = 'DONE!'
        key = key if key!=' ' else 'SPACE'
        print(key,end='')

    def calc_stroke(self):
        self.stroke = self.position // self.width

    @staticmethod
    def set_pos(x,y):
        print(Cursor.POS(x, y), end='')

    def print_next_char(self):
        if (self.stroke+1)*self.width < len(self.type_string):
            self.set_pos(self.width, self.TYPING_FORM+1)
            print(f'{Fore.YELLOW}{self.type_string[(self.stroke + 1) * self.width]}{Style.RESET_ALL}')

    def make_string(self):
        work_string = ''
        self.calc_stroke()
        part = slice(self.stroke * self.width - bool(self.stroke), (self.stroke + 1) * self.width)
        type_string = self.type_string[part]
        _params = self._params[part]
        for i, param in enumerate(_params):
            work_string += param + type_string[i] + Style.RESET_ALL
        work_string += type_string[len(_params):]
        return work_string

    def update_typing(self, reversed=False,**kwargs):
        self.print_formatted()
        self.print_letter()
        self.print_next_char()
        self.show_errors(kwargs.get('color'),kwargs.get('key'))
        self.set_pos(self.position+2-reversed, self.TYPING_FORM)

    def show_errors(self, color, key: Key|KeyCode):
        self.set_pos(1, self.ERROR_FORM)
        self.clear_line()
        char = key.char if isinstance(key,KeyCode) else key.name.upper()
        error = ''
        if color == Fore.RED: error = " !ERROR! "
        print(f'{color}{error}{Fore.CYAN}{char}{color}{error}{Style.RESET_ALL}')

    def start_new_typing(self):
        self.position = 0
        self._params = []
        self.type_string = random.choice(self.type_strings)
        self.clear_screen()
        self.print_formatted()
        self.print_letter()
        self.info_text = f'Terminal size({self.width},{self.height})'
        self.print_info()
        self.end_typing = False
        self.info_text = 'Start new game! Good luck!'

    def on_press(self,key: KeyCode | Key):
        self.print_info()
        # match key:
        color = None
        if key == Key.backspace:
            self.position -= 1
            if len(self._params) != 0:
                self._params.pop(-1)
            self.update_typing(reversed=True, color=Fore.YELLOW, key=key)
            return
        elif str(key) == '\x03' or key == Key.esc:
            return False
        elif self.position == len(self.type_string):
            self.end_typing = True
            self.info_text = 'You complete this text, do you want start new? Press right alt'
            return
        elif key == Key.shift:
            return
        elif isinstance(key,KeyCode) and key == KeyCode(char=self.type_string[self.position]):
            color = Fore.GREEN
        elif key == Key.alt_r and self.end_typing:
            self.start_new_typing()
            return
        elif key == Key.space and self.type_string[self.position] == ' ':
            color = Fore.GREEN
        elif isinstance(key, Key) and key != key.space:
            return
        else:
            color = Fore.RED
        # print('\n'+str(key) + '  ' + self.type_string[self.position] + ' '
        # +str(self.position) + '\n' + self.type_string)
        self._params.append(color)
        self.update_typing(color=color, key=key)
        self.position += 1
        # print(Cursor.FORWARD(self.position), end='')

    def __init__(self):
        self.width = shutil.get_terminal_size()[0]
        self.height = shutil.get_terminal_size()[1]
        with open('sampels.txt','r',encoding='utf-8') as f:
            self.type_strings = [i.strip() for i in f.read().split('\n') if i]
        self.start_new_typing()
        listener = Listener(
            on_press=self.on_press,
            on_release=lambda key: ...
        )
        with listener as listen:
            listen.join()
        self.clear_screen()
        self.set_pos(1,1)


Typer()


