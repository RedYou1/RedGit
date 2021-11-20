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
from git.diff import Diff

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
    if pat == path:
        if len(pats) <= 1:
            pats = []
            return True
        else:
            pat = pats[pats.index(path)-1]
    pats.remove(path)
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


class File():
    def __init__(self,a_path:str,b_path:str,a_content:list[str],b_content:list[str]):
        self.a_path:str = a_path
        self.b_path:str = b_path
        self.a_content:list[str] = a_content
        self.b_content:list[str] = b_content

    def Now(file:str):
        return File(None,file,None,ReadFile(file).split('\n'))

    def FromDiff(diff:Diff):
        file2:list[str] = None
        if exists(path()+"\\"+diff.b_path):
            file2:list[str] = ReadFile(diff.b_path).split('\n')
            
        a_blob:list[str] = [""]
        if diff.a_blob:
            a_blob:list[str] = diff.a_blob.data_stream.read().decode('utf-8').split('\n')
        return File(diff.a_path,diff.b_path,a_blob,file2)
    
def ReadFile(__path:str) -> str:
    t = open(path()+"\\"+__path, "r")
    r = t.read()
    t.close()
    return r

def CommitContent(commitID:str,file:str) -> str:
    return repo().git.show(commitID,file,format='')