from subprocess import Popen


def kill_drivers(filename='kill_drivers.bat'):
    p = Popen(filename)
    stdout, stderr = p.communicate()

# kill_drivers()
