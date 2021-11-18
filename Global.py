from git import *
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from git.repo.base import *
from genericpath import *
from typing import *
from git.objects.base import *
from git.objects.commit import *
from git.refs.reference import *

pats:list[str] = []
pat:str = None
rep:Repo = None

mainWindow:QMainWindow = None

def path() -> str:
    return pat

def paths() -> list[str]:
    return pats

def removePath(path:str) -> bool:
    global mainWindow
    global pat
    global pats
    pats.remove(path)
    if pat == path:
        if len(pats) == 0:
            return True
    return False

def repo() -> Repo:
    return rep

def setRepo(path:str):
    global rep
    global pat
    global pats
    rep = Repo(path+"\\.git")
    pat = path
    if not path in pats:
        pats.append(path)


def window() -> QMainWindow:
    return mainWindow

def setWindow(window:QMainWindow):
    global mainWindow
    mainWindow = window