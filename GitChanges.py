from genericpath import exists
from git.diff import Diff
from Global import *
import difflib

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

        if GitChanges.selected:
            file = QTextEdit()
            layout.addWidget(file)
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
            file.setText(text)

        if self.layout():
            QWidget().setLayout(self.layout())
        self.setLayout(layout)


class GitFiles(QVBoxLayout):
    def __init__(self,changes,branch):
        super().__init__()
        
        self.changes = changes
        self.files = [ item for item in repo.index.diff(branch) ]

        for file in self.files:
            self.addWidget(GitFile(self,File.FromDiff(file)))
        
        if branch == None:
            for file in repo.untracked_files:
                self.addWidget(GitFile(self,File.Now(file)))


class GitFile(QLabel):
    def __init__(self,files,file):
        super().__init__()

        self.files = files
        self.file = file

        if self.file.b_path:
            self.setText(self.file.b_path)
        else:
            self.setText(self.file.a_path)

        if GitChanges.selected and self.file == GitChanges.selected:
            self.setStyleSheet("background-color: cyan;")
    
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
            
        return File(diff.a_path,diff.b_path,diff.a_blob.data_stream.read().decode('utf-8').split('\n'),file2)

