from Global import *
from GitLog import *
from GitChanges import *
import easygui

def change_repo():
    window().hide()
    while True:
        string = easygui.diropenbox()
        try:
            setRepo(string)
            break
        except:
            pass
    w = window()
    w.show()
    w.activateWindow()
    w.main_win()

class Instance(QWidget):
    def __init__(self,p:str):
        super().__init__()

        self.path:str = p

        layout:QHBoxLayout = QHBoxLayout()

        label:QLabel = QLabel(p)
        if self.path == path():
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
        if removePath(self.path):
            change_repo()
        else:
            window().main_win()

    def mousePressEvent(self,e:QMouseEvent) -> None:
        setRepo(self.path)
        window().main_win()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RedGit")
        if repo():
            self.main_win()
        self.showMaximized()
    
    def main_win(self):
        mainLayout:QHBoxLayout = QHBoxLayout()

        midLayout:QVBoxLayout = QVBoxLayout()

        topLayout:QHBoxLayout = QHBoxLayout()
        for path in paths():
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

        midLayout.addLayout(topmidLayout)

        midLayout.addWidget(GitLog())
        midLayout.addWidget(GitChanges())
        mainLayout.addLayout(midLayout)
        container:QWidget = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def actuBut(self,e):
        self.main_win()
    
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
    if not repo():
        change_repo()
    app.exec()