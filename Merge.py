from Global import *


class MergeLayout(QWidget):
    def __init__(self,diff):
        super().__init__()

        self.diff:list[str] = diff
        self.selected:str = diff[0]

        self.Refresh()

    def Refresh(self):

        layout:QVBoxLayout = QVBoxLayout()

        top:QHBoxLayout = QHBoxLayout()
        
        for e in self.diff:
            but:QPushButton = QPushButton()
            but.setText(e)
            but.setCheckable(True)
            but.clicked.connect(self.changeFile)
            top.addWidget(but)

        layout.addLayout(top)

        mid:QHBoxLayout = QHBoxLayout()

        self.head1:QTextEdit = QTextEdit()
        self.head1.setText(CommitContent(repo().git.log("-1",source=True,format='oneline').split('\t')[0],self.selected))
        mid.addWidget(self.head1)

        self.head2:QTextEdit = QTextEdit()
        self.head2.setText(CommitContent(repo().git.log("-1",merge=True,source=True,format='oneline').split('\t')[0],self.selected))
        mid.addWidget(self.head2)

        layout.addLayout(mid)

        self.final:QTextEdit = QTextEdit()
        self.final.setText(ReadFile(self.selected))
        self.final.textChanged.connect(self.textChanged)
        layout.addWidget(self.final)

        buttons:QHBoxLayout = QHBoxLayout()

        abort:QPushButton = QPushButton()
        abort.setCheckable(True)
        abort.setText("Abort")
        abort.clicked.connect(self.abort)
        buttons.addWidget(abort)

        validate:QPushButton = QPushButton()
        validate.setText("Validate")
        validate.setCheckable(True)
        validate.clicked.connect(self.validate)
        buttons.addWidget(validate)

        layout.addLayout(buttons)


        if self.layout():
            QWidget().setLayout(self.layout())
        self.setLayout(layout)

    def textChanged(self):
        file = open(path()+"\\"+self.selected, "w")
        file.write(self.final.toPlainText())
        file.close()

    def validate(self,e):
        repo().git.add(self.selected)
        window().Refresh()

    def changeFile(self,e):
        self.selected = self.sender().text()
        self.Refresh()

    def abort(self,e):
        repo().git.merge(abort=True)
        window().Refresh()


