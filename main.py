from app import ControllerApp

if __name__ == '__main__':
    import sys
    c = ControllerApp()
    sys.exit(c.cmdloop())