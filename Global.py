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


class File():
    def __init__(self,a_path:str,b_path:str,a_content:list[str],b_content:list[str]):
        self.a_path:str = a_path
        self.b_path:str = b_path
        self.a_content:list[str] = a_content
        self.b_content:list[str] = b_content

    def Now(file:str):
        return File(None,file,None,Setting.ReadFile(file).split('\n'))

    def FromDiff(diff:Diff):
        file2:list[str] = None
        if exists(Setting.getInstance()+"\\"+diff.b_path):
            file2:list[str] = Setting.ReadFile(diff.b_path).split('\n')
            
        a_blob:list[str] = [""]
        if diff.a_blob:
            try:
                a_blob:list[str] = diff.a_blob.data_stream.read().decode('utf-8').split('\n')
            except Exception:
                a_blob:list[str] = ["Can't read"]
        return File(diff.a_path,diff.b_path,a_blob,file2)

class Setting():
    repo:Repo = None
    window:QMainWindow = None
    file_setting:str = os.getcwd()+"/settings.txt"
    __instance:str = None
    themeName:str = ""
    themes:list[str] = ["Dark","Default"]
    themePath:str = os.getcwd()+"/Themes/"
    showFolder:bool = False

    def ReadFile(__path:str) -> str:
        try:
            t = open(Setting.getInstance()+"\\"+__path, "r",encoding="utf-8")
            r = t.read()
            t.close()
        except Exception:
            r = "Can't read"
        return r

    def CommitContent(commitID:str,file:str) -> str:
        return Setting.repo.git.show(commitID,file,format='')

    def instances() -> list[str]:
        file = open(Setting.file_setting,'r')
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
        return Setting.__instance
    
    def setTheme(name:str):
        Setting.themeName = name
        file = open(Setting.file_setting,'r')
        lines = file.readlines()
        file.close()
        i = 0
        while not lines[i].startswith("Theme:"):
            i += 1
        lines.remove(lines[i])
        lines.insert(i,"Theme:"+name+'\n')
        file = open(Setting.file_setting,'w')
        file.writelines(lines)
        file.close()
        Setting.themes.remove(name)
        Setting.themes.insert(0,name)

    def getThemeCode() -> str:
        if not exists(Setting.themePath+Setting.themeName+".qss"):
            return ""
        
        file = open(Setting.themePath+Setting.themeName+".qss",'r')
        style = "".join(file.readlines())
        file.close()
        return style

    def refreshTheme() -> str:
        file = open(Setting.file_setting,'r')
        lines = file.readlines()
        i = 0
        while not lines[i].startswith("Theme:"):
            i += 1
        file.close()
        line = lines[i].removeprefix("Theme:").removesuffix('\n')
        if line == "":
            line = None
        Setting.themeName = line
        Setting.themes.remove(line)
        Setting.themes.insert(0,line)
        return line

    def refreshInstance() -> str:
        file = open(Setting.file_setting,'r')
        lines = file.readlines()
        i = 0
        while not lines[i].startswith("Instance:"):
            i += 1
        file.close()
        line = lines[i].removeprefix("Instance:").removesuffix('\n')
        if line == "":
            line = None
        Setting.__instance = line
        return line
    
    def setInstance(instance:str):
        Setting.repo = Repo(instance+"\\.git")
        Setting.__instance = instance
        file = open(Setting.file_setting,'r')
        lines = file.readlines()
        file.close()
        i = 0
        while not lines[i].startswith("Instance:"):
            i += 1
        lines.remove(lines[i])
        lines.insert(i,"Instance:"+instance+'\n')
        file = open(Setting.file_setting,'w')
        file.writelines(lines)
        file.close()
        if not instance in Setting.instances():
            Setting.addInstance(instance)

    def addInstance(instance:str):
        file = open(Setting.file_setting,'r')
        lines = file.readlines()
        file.close()
        lines.insert(lines.index("Instances:\n")+1,instance+'\n')
        file = open(Setting.file_setting,'w')
        file.writelines(lines)
        file.close()

    def removeInstance(instance:str) -> bool:
        file = open(Setting.file_setting,'r')
        lines = file.readlines()
        file.close()
        lines.remove(instance+'\n')
        if "Instance:"+instance in lines:
            ins = Setting.instances()
            if len(ins) == 0:
                file.close()
                return True
            lines.insert(lines.index("Instance:"+instance+'\n'),"Instance:"+ins[0])
            lines.remove("Instance:"+instance+'\n')
            Setting.__instance = ins[0].removesuffix('\n')
        file = open(Setting.file_setting,'w')
        file.writelines(lines)
        file.close()
        return False

if not exists(Setting.file_setting):
    file = open(Setting.file_setting,'w')
    file.write("Instance:\nInstances:\nTheme:Default\n")
    file.close()

Setting.refreshInstance()
Setting.refreshTheme()