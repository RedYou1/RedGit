from Global import *

class GitLog(QScrollArea):

    lineHeight = 30

    def __init__(self):
        super().__init__()

        self.selected = ""

        self.repo_commits = list(repo.iter_commits('--all'))

        self.view = QHBoxLayout()

        self.branchs = repo.refs
        self.commits = {}
        container = QWidget()
        container.setLayout(self.view)
        container.setFixedSize(1500,len(self.repo_commits)*GitLog.lineHeight)
        self.setWidget(container)

        self.columns = []
        self.branchs_commits = []

        self.nom_heads = QVBoxLayout()
        self.nom_commits = QVBoxLayout()
        self.nom_authors = QVBoxLayout()
        self.id_commits = QVBoxLayout()

        temp = self.branchs
        if repo.head.is_detached:
            temp.append(repo.head)

        for branch in self.branchs:
            col = []
            commits = list(repo.iter_commits(rev=branch))
            for com in commits:
                col.append(com)
            if len(col) != 0:
                self.columns.insert(0,branch)
                self.branchs_commits.insert(0,col)

        self.row = {}

        max = 0
        y = 0
        for com in self.repo_commits:
            if not com.hexsha in self.commits:

                style = "border:1px solid black;"
                
                if com.hexsha == self.selected:
                    style += "background-color: cyan;"
                elif com.hexsha == repo.head.commit.hexsha:
                    style += "background-color: lightgreen;"


                temp = QHBoxLayout()
                for i in range(len(self.columns)):
                    if com == self.branchs_commits[i][0]:
                        t = QLabel(self.columns[i].name)
                        tstyle = "border:hidden;"
                        if (repo.head.is_detached and self.columns[i].name == "HEAD") or \
                            (not repo.head.is_detached and self.columns[i] == repo.head.ref):
                            tstyle += "font-weight: bold;"
                        t.setStyleSheet(tstyle)
                        temp.addWidget(t)
                wid = QWidget()
                wid.setLayout(temp)
                wid.setFixedHeight(GitLog.lineHeight)
                wid.setStyleSheet(style)
                wid.mousePressEvent = self.commitMousePress
                self.nom_heads.addWidget(wid)
                temp = temp.count()
                if max < temp:
                    max = temp
                nom_commit = QLabel(com.message.split('\n')[0])
                nom_commit.setFixedHeight(GitLog.lineHeight)
                nom_commit.setStyleSheet(style)
                nom_commit.mousePressEvent = self.commitMousePress
                self.nom_commits.addWidget(nom_commit)
                author_name = QLabel(com.author.name)
                author_name.setFixedHeight(GitLog.lineHeight)
                author_name.setStyleSheet(style)
                author_name.mousePressEvent = self.commitMousePress
                self.nom_authors.addWidget(author_name)
                hex = QLabel(com.hexsha)
                hex.setFixedHeight(GitLog.lineHeight)
                hex.setStyleSheet(style)
                hex.mousePressEvent = self.commitMousePress
                self.id_commits.addWidget(hex)

                self.row[y] = [com.hexsha,wid,nom_commit,author_name,hex]
                self.row[com.hexsha] = [y,wid,nom_commit,author_name,hex]
                y+=1

        self.cercle = self.Cercles(self)
        self.view.addLayout(self.nom_heads)
        self.view.addWidget(self.cercle)
        self.view.addLayout(self.nom_commits)
        self.view.addLayout(self.nom_authors)
        self.view.addLayout(self.id_commits)

    def contextMenuEvent(self, event):
        if len(repo.index.diff(None)) == 0:
            contextMenu = QMenu(self)
            checkouts = []
            checkout = contextMenu.addMenu("Checkout")
            checkout_commit = checkout.addAction("this commit")
            for i in range(len(self.columns)):
                if self.selected == self.branchs_commits[i][0].hexsha and self.columns[i].name != "HEAD" and self.columns[i] in repo.branches:
                    checkouts.append(checkout.addAction(self.columns[i].name))
            action = contextMenu.exec_(self.mapToGlobal(event.pos()))
            w = window()
            if action == checkout_commit:
                repo.git.checkout(self.selected)
                w.main_win()
            if action in checkouts:
                repo.git.checkout(action.text())
                w.main_win()


    def commitMousePress(self,e:QMouseEvent):
        if self.selected in self.row:
            ele = self.row[self.selected]
            for i in range(1,len(ele)):
                style = "border:1px solid black;"
                if self.selected == repo.head.commit.hexsha:
                    style += "background-color: lightgreen;"
                ele[i].setStyleSheet(style)
        self.selected = self.row[int((e.globalY()-self.y()+self.verticalScrollBar().value())/GitLog.lineHeight)-1][0]
        ele = self.row[self.selected]
        for i in range(1,len(ele)):
            ele[i].setStyleSheet("border:1px solid black;background-color: cyan;")
        self.cercle.repaint()

    class Cercles(QWidget):
        def __init__(self,log):
            super().__init__()

            self.log = log

            self.commit = {}
            y = 0
            for com in self.log.repo_commits:
                if not com.hexsha in self.log.commits:
                    i = 0
                    for e in range(len(self.log.columns)):
                        if com in self.log.branchs_commits[e]:
                            i = e
                            break
                    self.commit[com.hexsha] = [com,y,QPoint(i*GitLog.lineHeight/2+GitLog.lineHeight/4,y*GitLog.lineHeight+GitLog.lineHeight/2)]
                    y += 1

        def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
            for com in self.commit:
                commit = self.commit[com]
                commit[2] = QPoint(commit[2].x(),commit[1]*GitLog.lineHeight+GitLog.lineHeight/2)
            return super().resizeEvent(a0)

        def paintEvent(self,e):
            qp = QPainter(self)
            for com in self.log.repo_commits:
                if not com.hexsha in self.log.commits:
                    a = False
                    if com.hexsha == self.log.selected:
                        a=True
                        qp.setBrush(QBrush(Qt.cyan))
                    elif com.hexsha == repo.head.commit.hexsha:
                        a=True
                        qp.setBrush(QBrush(Qt.green))
                    qp.drawEllipse(self.commit[com.hexsha][2].x()-GitLog.lineHeight/4,self.commit[com.hexsha][2].y()-GitLog.lineHeight/4,GitLog.lineHeight/2,GitLog.lineHeight/2)
                    if a:
                        qp.setBrush(QBrush())
                for parent in com.parents:
                    qp.drawLine(self.commit[com.hexsha][2].x(),self.commit[com.hexsha][2].y(),
                        self.commit[parent.hexsha][2].x(),self.commit[parent.hexsha][2].y())
            qp.end()