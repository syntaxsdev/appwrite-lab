from subprocess import run, PIPE, STDOUT, CalledProcessError

class AppwriteLab:
    def __init__(self):
        self.labs = {}
        