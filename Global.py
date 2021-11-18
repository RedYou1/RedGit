from PyQt5 import QtGui
from git import *
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from git.repo.base import Repo

path:str = "C:\\Users\\jcdem\\OneDrive\\Bureau\\test git"
#__path = "C:\\Users\\jcdem\\OneDrive\\Bureau\\Godot\\GoBros"

rep:Repo = Repo(path+"\\.git")

mainWindow:QMainWindow = None

def repo() -> Repo:
    return rep

def setRepo(repo:Repo):
    global rep
    rep = repo

def window() -> QMainWindow:
    return mainWindow

def setWindow(window:QMainWindow):
    global mainWindow
    mainWindow = window