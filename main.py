from Global import *
from Merge import *
from Remote import *
from GitLog import *
from GitChanges import *
import easygui

def change_repo():
    window().hide()
    while True:
        string = easygui.diropenbox()
        if string == None:
            break
        try:
            setInstance(string)
            break
        except:
            pass
    if len(instances()) == 0:
        sys.exit()
    w = window()
    w.show()
    w.activateWindow()
    w.Refresh()

class Instance(QWidget):
    def __init__(self,p:str):
        super().__init__()

        self.path:str = p

        layout:QHBoxLayout = QHBoxLayout()

        label:QLabel = QLabel(p)
        if self.path == getInstance():
            label.setStyleSheet("background-color: cyan;")
        else:
            label.setStyleSheet("background-color: lightgray;")
        layout.addWidget(label)

        remove:QPushButton = QPushButton()
        remove.setCheckable(True)
        remove.setText("X")
        remove.clicked.connect(self.remove)
        layout.addWidget(remove)

        self.setLayout(layout)
    
    def remove(self, e):
        if removeInstance(self.path):
            change_repo()
        else:
            window().main_win()

    def mousePressEvent(self,e:QMouseEvent) -> None:
        setInstance(self.path)
        window().main_win()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected = self.main_win
        self.setWindowTitle("RedGit")
        self.showMaximized()
    
    def Refresh(self):
        if repo():
            diff:str = repo().git.diff(name_only=True,diff_filter='U')
            if diff != "":
                self.selected = self.main_win
                self.merge_win(diff.split('\n'))
            else:
                self.selected()

    def remotes_win(self):
        mainLayout:QVBoxLayout = QVBoxLayout()

        mainLayout.addLayout(RemoteLayout(self))

        container:QWidget = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def merge_win(self,diff:list[str]):
        mainLayout:QVBoxLayout = QVBoxLayout()

        mainLayout.addWidget(MergeLayout(diff))

        container:QWidget = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def main_win(self):
        mainLayout:QHBoxLayout = QHBoxLayout()

        midLayout:QVBoxLayout = QVBoxLayout()

        topLayout:QHBoxLayout = QHBoxLayout()
        for path in instances():
            topLayout.addWidget(Instance(path))
        
        add = QPushButton()
        add.setCheckable(True)
        add.setText("+")
        add.clicked.connect(change_repo)
        topLayout.addWidget(add)

        midLayout.addLayout(topLayout)

        topmidLayout:QHBoxLayout = QHBoxLayout()
        actu:QPushButton = QPushButton()
        actu.setText("Actualiser")
        actu.setCheckable(True)
        actu.clicked.connect(self.actuBut)
        topmidLayout.addWidget(actu)

        actu:QPushButton = QPushButton()
        actu.setText("Stash")
        actu.setCheckable(True)
        actu.clicked.connect(self.Stash)
        topmidLayout.addWidget(actu)

        actu:QPushButton = QPushButton()
        actu.setText("UnStash")
        actu.setCheckable(True)
        actu.clicked.connect(self.UnStash)
        topmidLayout.addWidget(actu)

        actu:QPushButton = QPushButton()
        actu.setText("Remotes")
        actu.setCheckable(True)
        actu.clicked.connect(self.SetRemotes)
        topmidLayout.addWidget(actu)

        midLayout.addLayout(topmidLayout)

        midLayout.addWidget(GitLog())
        midLayout.addWidget(GitChanges())
        mainLayout.addLayout(midLayout)
        container:QWidget = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def SetMain(self,e):
        self.selected = self.main_win
        self.Refresh()

    def SetRemotes(self,e):
        self.selected = self.remotes_win
        self.Refresh()

    def actuBut(self,e):
        self.Refresh()
    
    def Stash(self,e):
        repo().git.stash('save')
        self.main_win()

    def UnStash(self,e):
        repo().git.stash('pop')
        self.main_win()

if __name__ == "__main__":
    app:QApplication = QApplication(sys.argv)
    mainWindow:MainWindow = MainWindow()
    setWindow(mainWindow)
    mainWindow.show()
    ins = getInstance()
    if ins != None:
        setInstance(ins)
        mainWindow.Refresh()
    else:
        change_repo()
    app.exec()