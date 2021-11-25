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
        self.unstaged:QScrollArea = QScrollArea()
        self.unstaged.setWidget(GitFiles(self,None))
        layout.addWidget(self.unstaged)
        self.staged:QScrollArea = QScrollArea()
        self.staged.setWidget(GitFiles(self,'HEAD'))
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
            for t in difflib.unified_diff(a=file1, b=file2,fromfile=name_file1,tofile=name_file2,lineterm=''):
                text += t + '\n'
            self.file.setText(text)

    def commit(self,e):
        Setting.repo.git.commit(self.message.text(),m=True)
        Setting.window.Refresh()


class GitFiles(QWidget):
    def __init__(self,changes:GitChanges,branch:str):
        super().__init__()
        
        layout:QVBoxLayout = QVBoxLayout()

        staged:bool = branch != None

        self.changes:GitChanges = changes
        self.files:list[Diff] = [ item for item in Setting.repo.index.diff(branch) ]

        for file in self.files:
            layout.addWidget(GitFile(self,File.FromDiff(file),staged))
        
        if not staged:
            for file in Setting.repo.untracked_files:
                layout.addWidget(GitFile(self,File.Now(file),False))
        
        self.setLayout(layout)


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

        if GitChanges.selected and self.file.a_path == GitChanges.selected.a_path and self.file.b_path == GitChanges.selected.b_path:
            label.setStyleSheet("background-color: cyan;")
    
    def stage(self,e):
        Setting.repo.git.add(self.file.b_path)
        self.files.changes.Refresh()

    def unStage(self,e):
        Setting.repo.git.restore(self.file.b_path,staged=True)
        self.files.changes.Refresh()

    def removed(self,e):
        if self.staged:
            self.unStage(None)
        if self.file.b_path in Setting.repo.untracked_files:
            os.remove(Setting.getInstance()+"\\"+self.file.b_path)
        else:
            Setting.repo.git.restore(self.file.b_path)
        self.files.changes.Refresh()

    def mousePressEvent(self,e:QMouseEvent):
        GitChanges.selected = self.file
        self.files.changes.Refresh()

