from PyQt5 import QtGui, QtWidgets
from Global import *
import difflib
import os

class GitChanges(QWidget):
    selected:File = None
    
    def __init__(self):
        super().__init__()

        self.Refresh()

    def Refresh(self):
        layout:QHBoxLayout = QHBoxLayout()

        option:QVBoxLayout = QVBoxLayout()
        byfolder:QPushButton = QPushButton()
        byfolder.setCheckable(True)
        byfolder.setText("By Folder")
        byfolder.clicked.connect(self.byfolder)
        option.addWidget(byfolder)
        layout.addLayout(option)

        layoutUnStage:QVBoxLayout = QVBoxLayout()
        stageall:QPushButton = QPushButton()
        stageall.setText("Stage All")
        stageall.setCheckable(True)
        stageall.clicked.connect(self.stageAll)
        layoutUnStage.addWidget(stageall)
        self.unstaged:QScrollArea = QScrollArea()
        self.unstaged.setWidget(GitFiles(self,None))
        layoutUnStage.addWidget(self.unstaged)
        layout.addLayout(layoutUnStage)

        layoutStage:QVBoxLayout = QVBoxLayout()
        unstageall:QPushButton = QPushButton()
        unstageall.setText("UnStage All")
        unstageall.setCheckable(True)
        unstageall.clicked.connect(self.unStageAll)
        layoutStage.addWidget(unstageall)
        self.staged:QScrollArea = QScrollArea()
        self.staged.setWidget(GitFiles(self,'HEAD'))
        layoutStage.addWidget(self.staged)
        layout.addLayout(layoutStage)

        
        temp:QVBoxLayout = QVBoxLayout()
        layout.addLayout(temp)
        self.message:QLineEdit = QLineEdit()
        temp.addWidget(self.message)
        self.file:QTextEdit = QTextEdit()
        temp.addWidget(self.file)
        self.actuText()

        but:QPushButton = QPushButton()
        but.setText("Commit")
        but.setCheckable(True)
        but.clicked.connect(self.commit)
        temp.addWidget(but)

        if self.layout():
            QWidget().setLayout(self.layout())
        self.setLayout(layout)

    def byfolder(self,e):
        Setting.showFolder = not Setting.showFolder
        self.Refresh()

    def stageAll(self,e):
        Setting.repo.git.add('.')
        self.Refresh()

    def unStageAll(self,e):
        Setting.repo.git.restore('.',staged=True)
        self.Refresh()

    def actuText(self):
        if GitChanges.selected:
            name_file1:str = ""
            name_file2:str = ""
            file1:list[str] = []
            file2:list[str] = []
            if GitChanges.selected.a_content:
                name_file1:str = GitChanges.selected.a_path
                file1:list[str] = GitChanges.selected.a_content
            if GitChanges.selected.b_content:
                name_file2:str = GitChanges.selected.b_path
                file2:list[str] = GitChanges.selected.b_content
            text:str = ""
            for t in difflib.unified_diff(a=file1, b=file2,fromfile=name_file1,tofile=name_file2,lineterm=''):
                text += t + '\n'
            self.file.setText(text)

    def commit(self,e):
        Setting.repo.git.commit(self.message.text(),m=True)
        Setting.window.Refresh()


class GitFiles(QWidget):
    def __init__(self,changes:GitChanges,branch:str):
        super().__init__()
        
        self.setObjectName("GitFiles")
        
        layout:QVBoxLayout = QVBoxLayout()

        self.staged:bool = branch != None

        self.changes:GitChanges = changes
        self.files:list[Diff] = [ item for item in Setting.repo.index.diff(branch) ]

        if Setting.showFolder:            
            self.folder = {}
            
            def merge(dict1:dict,dict2:dict) -> dict:
                for key in dict2:
                    if key in dict1:
                        dict1[key] = merge(dict1[key],dict2[key])
                    else:
                        dict1[key] = dict2[key]
                return dict1
            
            def into_folder(file:File):
                path:list[str] = []
                if file.b_path:
                    path = file.b_path.split('/')
                else:
                    path = file.a_path.split('/')
                
                path.pop()
                
                if len(path) > 0:
                    temp:Union[GitFile,dict[str,File],dict[str,dict]] = file
                    
                    for i in range(len(path)-1,-1,-1):
                        temp = {path[i]:temp}
                    self.folder = merge(self.folder,temp)
                else:
                    layout.addWidget(GitFile(self,file))
            
            for file in self.files:
                into_folder(File.FromDiff(file))
                
            if not self.staged:
                for file in Setting.repo.untracked_files:
                    into_folder(File.Now(file))
            
            def cleaning_folder(folder:dict) -> dict:
                while len(folder) == 1:
                    key:str = list(folder.keys())[0]
                    if isinstance(folder[key],dict) and len(folder[key]) == 1:
                        nkey = key+'/'+list(folder[key].keys())[0]
                        folder[nkey] = folder[key][list(folder[key].keys())[0]]
                        folder.pop(key)
                    else:
                        break
                
                for key in folder:
                    if isinstance(folder[key],dict):
                        folder[key] = cleaning_folder(folder[key])
                
                return folder
            
            self.folder = cleaning_folder(self.folder)
            
            def dict_gitfolder(d:dict,name:str) -> Tuple[list,str]:
                l = []
                for key in d:
                    if isinstance(d[key],dict):
                        l.append(dict_gitfolder(d[key],key))
                    else:
                        l.append(d[key])
                return (l,name)
            
            for key in self.folder:
                a = dict_gitfolder(self.folder[key],key)
                layout.addWidget(GitFolder(self,a[0],a[1],False))
        else:
            for file in self.files:
                layout.addWidget(GitFile(self,File.FromDiff(file)))
        
            if not self.staged:
                for file in Setting.repo.untracked_files:
                    layout.addWidget(GitFile(self,File.Now(file)))
        
        self.setLayout(layout)   

class GitFile(QWidget):
    def __init__(self,files:GitFiles,file:File):
        super().__init__()

        layout:QHBoxLayout = QHBoxLayout()
        label:QLabel = QLabel()

        self.files:GitFiles = files
        self.file:File = file

        if self.file.b_path:
            label.setText(self.file.b_path)
        else:
            label.setText(self.file.a_path)

        layout.addWidget(label)

        remove:QPushButton = QPushButton()
        remove.setText("X")
        remove.setCheckable(True)
        remove.clicked.connect(self.removed)
        layout.addWidget(remove)

        if files.staged:
            s:QPushButton = QPushButton()
            s.setText("<")
            s.setCheckable(True)
            s.clicked.connect(self.unStage)
            layout.addWidget(s)
        else:
            s:QPushButton = QPushButton()
            s.setText(">")
            s.setCheckable(True)
            s.clicked.connect(self.stage)
            layout.addWidget(s)

        self.setLayout(layout)

        if GitChanges.selected and self.file.a_path == GitChanges.selected.a_path and self.file.b_path == GitChanges.selected.b_path:
            label.setObjectName("Instance_QLabel_Selected")
        else:
            label.setObjectName("Instance_QLabel")
    
    def stage(self,e):
        Setting.repo.git.add(self.file.b_path)
        self.files.changes.Refresh()

    def unStage(self,e):
        Setting.repo.git.restore(self.file.b_path,staged=True)
        self.files.changes.Refresh()

    def removed(self,e):
        if self.files.staged:
            self.unStage(None)
        if self.file.b_path in Setting.repo.untracked_files:
            os.remove(Setting.getInstance()+"\\"+self.file.b_path)
        else:
            Setting.repo.git.restore(self.file.b_path)
        self.files.changes.Refresh()

    def mousePressEvent(self,e:QMouseEvent):
        GitChanges.selected = self.file
        self.files.changes.Refresh()


class GitFolder(QWidget):    
    def __init__(self,parent:GitFiles,files:list[Union[File,Tuple[list,str]]],name:str,show:bool):
        super().__init__()
        self.shown = show
        self._parent = parent
        self.name = name
        self.files:list[Union[File,Tuple[list,str]]] = files
        self.setObjectName("GitFolder")
        self.Refresh()
        
    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.shown = not self.shown
        self.Refresh()
        return super().mousePressEvent(a0)
        
    def Refresh(self):
        layout:QVBoxLayout = QVBoxLayout()
        
        if self.shown:
            layout.addWidget(QLabel("[down]"+self.name))
        else:
            layout.addWidget(QLabel(">"+self.name))
        
        if self.shown:
            l:QVBoxLayout = QVBoxLayout()
            for e in self.files:
                if isinstance(e,File):
                    l.addWidget(GitFile(self._parent,e))
                else:
                    l.addWidget(GitFolder(self._parent,e[0],e[1],False))
            layout.addLayout(l)
            
        
        if self.layout():
            QWidget().setLayout(self.layout())
        self.setLayout(layout)
