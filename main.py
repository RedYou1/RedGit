from Global import *
from GitLog import *
from GitChanges import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RedGit")
        self.main_win()
        self.showMaximized()
    
    def main_win(self):
        mainLayout:QHBoxLayout = QHBoxLayout()
        midLayout:QVBoxLayout = QVBoxLayout()

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


def main():
    app:QApplication = QApplication(sys.argv)

    mainWindow:MainWindow = MainWindow()
    mainWindow.show()

    setWindow(mainWindow)

    app.exec()

if __name__ == "__main__":
    main()