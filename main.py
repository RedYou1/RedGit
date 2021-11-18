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
        mainLayout = QHBoxLayout()
        midLayout = QVBoxLayout()

        actu = QPushButton()
        actu.setText("Actualiser")
        actu.setCheckable(True)
        actu.clicked.connect(self.actuBut)
        midLayout.addWidget(actu)

        midLayout.addWidget(GitLog())
        midLayout.addWidget(GitChanges())
        mainLayout.addLayout(midLayout)
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def actuBut(self,e):
        self.main_win()

def main():
    app = QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.show()

    setWindow(mainWindow)

    app.exec()

if __name__ == "__main__":
    main()