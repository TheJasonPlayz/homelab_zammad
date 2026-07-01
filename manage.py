#!python
from argparse import ArgumentParser, Namespace
from glob import glob
from pathlib import Path
import subprocess

CHOICES = ['up', 'down', 'restart', 'logs']

class DockerManager():
    parser: ArgumentParser
    args: Namespace
    files: list[Path] = []
    env_file: Path = Path()
    build: bool

    def __setup_argparse(self, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument("-a", "--action", choices=CHOICES)
        parser.add_argument("files", nargs='*', default='**/docker-compose.yml', type= lambda x: Path(x))
        parser.add_argument("-b", "--build", action='store_true')
        return parser

    
    def __init__(self):
        parser = ArgumentParser(
            prog='Docker Manager',
            description='A python program to manage docker containers using compose files.')
        self.args = self.__setup_argparse(parser).parse_args()
        self.files = self.get_files()
        self.build = self.args.build

    def check_env(self, compose_file: Path):
        parent_dir = compose_file.parent
        parent_env = (parent_dir / ".env")
        if parent_env.is_file():
            self.env_file = parent_env
        else:
            self.env_file = Path('./.default/.env')

    def generate_base_cmd(self, action: str, file: Path) -> list[str]:
        cmd = ['docker', 'compose', '--env-file', str(self.env_file.resolve()),'-f', str(file.resolve()), action]
        if self.args.build:
            cmd.append("--build")
        return cmd

    def get_files(self):
        if self.args.files == '**/docker-compose.yml':
            print(self.args.files)
            return [Path(file) for file in glob(self.args.files, recursive=True)]
        else:
            return [file.resolve() for path in self.args.files for file in path.glob('**/docker-compose.yml')]
                
    
    def execute(self):
        for file in self.files:
            self.check_env(file)
            self.execute_action(file)
    
    def run_cmd(self, cmd: list[str], dir: Path):
        print(" ".join(cmd))
        log_file = open(f"./.logs/{dir.name}.log", 'w')
        process = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            cwd=dir)
        log_file.close()
        return process

    def execute_action(self, file: Path):
        choice = self.args.action
        match (choice):
            case 'up':
                return self.execute_up(file)
            case 'down':
                return self.execute_down(file)
            case 'restart':
                return self.execute_restart(file)
            case 'logs':
                return self.execute_logs(file)
            case _:
                return ValueError('Choice not found!')
                
    def execute_up(self, file: Path):
        cmd = self.generate_base_cmd('up', file)
        self.run_cmd(cmd, file.parent)

    def execute_down(self, file: Path):
        cmd = self.generate_base_cmd('down', file)
        self.run_cmd(cmd, file.parent)

    def execute_restart(self, file: Path):
        down = self.execute_down(file)
        up = self.execute_up(file)
        return (down, up)

    def execute_logs(self, file: Path):
        cmd = self.generate_base_cmd('logs', file)
        self.run_cmd(cmd, file.parent)

if __name__ == "__main__":
    manager = DockerManager()
    print(manager.execute())