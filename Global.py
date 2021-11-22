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
import os

rep:Repo = None

mainWindow:QMainWindow = None

def repo() -> Repo:
    return rep

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
        if exists(getInstance()+"\\"+diff.b_path):
            file2:list[str] = ReadFile(diff.b_path).split('\n')
            
        a_blob:list[str] = [""]
        if diff.a_blob:
            a_blob:list[str] = diff.a_blob.data_stream.read().decode('utf-8').split('\n')
        return File(diff.a_path,diff.b_path,a_blob,file2)
    
def ReadFile(__path:str) -> str:
    t = open(getInstance()+"\\"+__path, "r")
    r = t.read()
    t.close()
    return r

def CommitContent(commitID:str,file:str) -> str:
    return repo().git.show(commitID,file,format='')


__settings:str = os.getcwd()+"/settings.txt"

if not exists(__settings):
    file = open(__settings,'w')
    file.write("Instance:\nInstances:\nTheme:")
    file.close()

def instances() -> list[str]:
    global __settings
    file = open(__settings,'r')
    lines = file.readlines()
    result:list[str] = []
    while not lines.pop(0).startswith("Instances:"):
        pass
    line = lines.pop(0)
    while not line.startswith("Theme:"):
        result.append(line.removesuffix('\n'))
        line = lines.pop(0)
    file.close()
    return result

def getInstance() -> str:
    global __settings
    file = open(__settings,'r')
    lines = file.readlines()
    i = 0
    while not lines[i].startswith("Instance:"):
        i += 1
    file.close()
    line = lines[i].removeprefix("Instance:").removesuffix('\n')
    if line == "":
        line = None
    return line
    
def setInstance(instance:str):
    global __settings
    global rep
    rep = Repo(instance+"\\.git")
    file = open(__settings,'r')
    lines = file.readlines()
    file.close()
    i = 0
    while not lines[i].startswith("Instance:"):
        i += 1
    lines.remove(lines[i])
    lines.insert(i,"Instance:"+instance+'\n')
    file = open(__settings,'w')
    file.writelines(lines)
    file.close()
    if not instance in instances():
        addInstance(instance)

def addInstance(instance:str):
    global __settings
    file = open(__settings,'r')
    lines = file.readlines()
    file.close()
    lines.insert(lines.index("Instances:\n")+1,instance+'\n')
    file = open(__settings,'w')
    file.writelines(lines)
    file.close()

def removeInstance(instance:str) -> bool:
    global __settings
    file = open(__settings,'r')
    lines = file.readlines()
    file.close()
    lines.remove(instance+'\n')
    if "Instance:"+instance in lines:
        ins = instances()
        if len(ins) == 0:
            file.close()
            return True
        lines.insert(lines.index("Instance:"+instance+'\n'),"Instance:"+ins[0])
        lines.remove("Instance:"+instance+'\n')
    file = open(__settings,'w')
    file.writelines(lines)
    file.close()
    return False