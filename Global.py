from PyQt5 import QtGui
import git
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

path = "C:\\Users\\jcdem\\OneDrive\\Bureau\\test git"
#path = "C:\\Users\\jcdem\\OneDrive\\Bureau\\Godot\\GoBros"

repo = git.Repo(path+"\\.git")

mainWindow = None

def window():
    return mainWindow
def setWindow(window):
    global mainWindow
    mainWindow = window