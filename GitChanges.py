from genericpath import exists
from git.diff import Diff
from Global import *
import difflib
import os

class File():
    def __init__(self,a_path:str,b_path:str,a_content:list[str],b_content:list[str]):
        self.a_path:str = a_path
        self.b_path:str = b_path
        self.a_content:list[str] = a_content
        self.b_content:list[str] = b_content

    def Now(file:str):    
        fileb = open(path+"\\"+file, "r")
        file2 = fileb.read().split('\n')
        fileb.close()
        return File(None,file,None,file2)

    def FromDiff(diff:Diff):

        file2:list[str] = None
        if exists(path+"\\"+diff.b_path):
            fileb = open(path+"\\"+diff.b_path, "r")
            file2:list[str] = fileb.read().split('\n')
            fileb.close()
            
        a_blob:list[str] = [""]
        if diff.a_blob:
            a_blob:list[str] = diff.a_blob.data_stream.read().decode('utf-8').split('\n')
        return File(diff.a_path,diff.b_path,a_blob,file2)

class GitChanges(QWidget):
    selected:File = None
    def __init__(self):
        super().__init__()
        self.Refresh()

    def Refresh(self):
        layout:QHBoxLayout = QHBoxLayout()
        self.unstaged:QScrollArea = QScrollArea()
        self.unstaged.setLayout(GitFiles(self,None))
        layout.addWidget(self.unstaged)
        self.staged:QScrollArea = QScrollArea()
        self.staged.setLayout(GitFiles(self,'HEAD'))
        layout.addWidget(self.staged)

        
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
            for t in difflib.unified_diff(file1, file2,name_file1,name_file2):
                text += t
                if not t.endswith('\n'):
                    text += '\n'
            self.file.setText(text)

    def commit(self,e):
        repo().git.commit(self.message.text(),m=True)
        window().main_win()


class GitFiles(QVBoxLayout):
    def __init__(self,changes:GitChanges,branch:str):
        super().__init__()
        
        staged:bool = branch != None

        self.changes:GitChanges = changes
        self.files:list[Diff] = [ item for item in repo().index.diff(branch) ]

        for file in self.files:
            self.addWidget(GitFile(self,File.FromDiff(file),staged))
        
        if not staged:
            for file in repo().untracked_files:
                self.addWidget(GitFile(self,File.Now(file),False))


class GitFile(QWidget):
    def __init__(self,files:GitFiles,file:File,staged:bool):
        super().__init__()

        self.staged:bool = staged
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

        if staged:
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

        if GitChanges.selected and self.file == GitChanges.selected:
            self.setStyleSheet("background-color: cyan;")
    
    def stage(self,e):
        repo().git.add(self.file.b_path)
        self.files.changes.Refresh()

    def unStage(self,e):
        repo().git.restore(self.file.b_path,staged=True)
        self.files.changes.Refresh()

    def removed(self,e):
        if self.staged:
            self.unStage(None)
        if self.file.b_path in repo().untracked_files:
            os.remove(path+"\\"+self.file.b_path)
        else:
            repo().git.restore(self.file.b_path)
        self.files.changes.Refresh()

    def mousePressEvent(self,e:QMouseEvent):
        GitChanges.selected = self.file
        self.files.changes.Refresh()

