from genericpath import exists
from git.diff import Diff
from Global import *
import difflib
import os

class GitChanges(QWidget):
    selected = ""
    def __init__(self):
        super().__init__()
        self.Refresh()

    def Refresh(self):
        layout = QHBoxLayout()
        self.unstaged = QScrollArea()
        self.unstaged.setLayout(GitFiles(self,None))
        layout.addWidget(self.unstaged)
        self.staged = QScrollArea()
        self.staged.setLayout(GitFiles(self,'HEAD'))
        layout.addWidget(self.staged)

        
        temp = QVBoxLayout()
        layout.addLayout(temp)
        self.message = QLineEdit()
        temp.addWidget(self.message)
        self.file = QTextEdit()
        temp.addWidget(self.file)
        self.actuText()

        but = QPushButton()
        but.setText("Commit")
        but.setCheckable(True)
        but.clicked.connect(self.commit)
        temp.addWidget(but)

        if self.layout():
            QWidget().setLayout(self.layout())
        self.setLayout(layout)
    
    def actuText(self):
        if GitChanges.selected:
            name_file1 = ""
            name_file2 = ""
            file1 = []
            file2 = []
            if GitChanges.selected.a_content:
                name_file1 = GitChanges.selected.a_path
                file1 = GitChanges.selected.a_content
            if GitChanges.selected.b_content:
                name_file2 = GitChanges.selected.b_path
                file2 = GitChanges.selected.b_content
            text = ""
            for t in difflib.unified_diff(file1, file2,name_file1,name_file2):
                text += t
                if not t.endswith('\n'):
                    text += '\n'
            self.file.setText(text)

    def commit(self,e):
        repo.git.commit(self.message.text(),m=True)
        window().main_win()


class GitFiles(QVBoxLayout):
    def __init__(self,changes,branch):
        super().__init__()
        
        staged = branch != None

        self.changes = changes
        self.files = [ item for item in repo.index.diff(branch) ]

        for file in self.files:
            self.addWidget(GitFile(self,File.FromDiff(file),staged))
        
        if not staged:
            for file in repo.untracked_files:
                self.addWidget(GitFile(self,File.Now(file),False))


class GitFile(QWidget):
    def __init__(self,files,file,staged):
        super().__init__()

        self.staged = staged
        layout = QHBoxLayout()
        label = QLabel()

        self.files = files
        self.file = file

        if self.file.b_path:
            label.setText(self.file.b_path)
        else:
            label.setText(self.file.a_path)

        layout.addWidget(label)

        remove = QPushButton()
        remove.setText("X")
        remove.setCheckable(True)
        remove.clicked.connect(self.removed)
        layout.addWidget(remove)

        if staged:
            s = QPushButton()
            s.setText("<")
            s.setCheckable(True)
            s.clicked.connect(self.unStage)
            layout.addWidget(s)
        else:
            s = QPushButton()
            s.setText(">")
            s.setCheckable(True)
            s.clicked.connect(self.stage)
            layout.addWidget(s)

        self.setLayout(layout)

        if GitChanges.selected and self.file == GitChanges.selected:
            self.setStyleSheet("background-color: cyan;")
    
    def stage(self,e):
        repo.git.add(self.file.b_path)
        self.files.changes.Refresh()

    def unStage(self,e):
        repo.git.restore(self.file.b_path,staged=True)
        self.files.changes.Refresh()

    def removed(self,e):
        if self.staged:
            self.unStage(None)
        if self.file.b_path in repo.untracked_files:
            os.remove(path+"\\"+self.file.b_path)
        else:
            repo.git.restore(self.file.b_path)
        self.files.changes.Refresh()

    def mousePressEvent(self,e:QMouseEvent):
        GitChanges.selected = self.file
        self.files.changes.Refresh()

class File():
    def __init__(self,a_path,b_path,a_content,b_content):
        self.a_path = a_path
        self.b_path = b_path
        self.a_content = a_content
        self.b_content = b_content

    def Now(file):        
        fileb = open(path+"\\"+file, "r")
        file2 = fileb.read().split('\n')
        fileb.close()
        return File(None,file,None,file2)

    def FromDiff(diff:Diff):

        file2 = None
        if exists(path+"\\"+diff.b_path):
            fileb = open(path+"\\"+diff.b_path, "r")
            file2 = fileb.read().split('\n')
            fileb.close()
            
        a_blob = ""
        if diff.a_blob:
            a_blob = diff.a_blob.data_stream.read().decode('utf-8').split('\n')
        return File(diff.a_path,diff.b_path,a_blob,file2)

