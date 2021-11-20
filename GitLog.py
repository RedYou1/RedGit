from PyQt5 import QtGui
from Global import *

class GitLog(QScrollArea):

    lineHeight:int = 30

    def __init__(self):
        super().__init__()

        self.selected:str = ""

        self.repo_commits:list[Commit] = list(repo().iter_commits('--all'))

        self.view:QHBoxLayout = QHBoxLayout()

        self.branchs:list[Reference] = repo().refs
        self.commits:dict[str,Commit] = {}
        container:QWidget = QWidget()
        container.setLayout(self.view)
        container.setFixedSize(1500,len(self.repo_commits)*GitLog.lineHeight)
        self.setWidget(container)

        self.columns:list[list[Commit]] = []
        self.branchs_commits:list[list[Commit]] = []

        self.nom_heads:QVBoxLayout = QVBoxLayout()
        self.nom_commits:QVBoxLayout = QVBoxLayout()
        self.nom_authors:QVBoxLayout = QVBoxLayout()
        self.id_commits:QVBoxLayout = QVBoxLayout()

        temp:list[Reference] = self.branchs
        if repo().head.is_detached:
            temp.append(repo().head)

        for branch in self.branchs:
            col:list[Commit] = []
            commits:list[Commit] = list(repo().iter_commits(rev=branch))
            for com in commits:
                col.append(com)
            if len(col) != 0:
                self.columns.insert(0,branch)
                self.branchs_commits.insert(0,col)

        self.row:dict[Union[int,str],list[Object]] = {}

        max:int = 0
        y:int = 0
        for com in self.repo_commits:
            if not com.hexsha in self.commits:

                style:str = "border:1px solid black;"
                
                if com.hexsha == self.selected:
                    style += "background-color: cyan;"
                elif com.hexsha == repo().head.commit.hexsha:
                    style += "background-color: lightgreen;"


                temp:QHBoxLayout = QHBoxLayout()
                for i in range(len(self.columns)):
                    if com == self.branchs_commits[i][0]:
                        t:QLabel = QLabel(self.columns[i].name)
                        tstyle:str = "border:hidden;"
                        if (repo().head.is_detached and self.columns[i].name == "HEAD") or \
                            (not repo().head.is_detached and self.columns[i] == repo().head.ref):
                            tstyle += "font-weight: bold;"
                        t.setStyleSheet(tstyle)
                        temp.addWidget(t)
                wid:QWidget = QWidget()
                wid.setLayout(temp)
                wid.setFixedHeight(GitLog.lineHeight)
                wid.setStyleSheet(style)
                wid.mousePressEvent = self.commitMousePress
                self.nom_heads.addWidget(wid)
                temp:int = temp.count()
                if max < temp:
                    max:int = temp
                nom_commit:QLabel = QLabel(com.message.split('\n')[0])
                nom_commit.setFixedHeight(GitLog.lineHeight)
                nom_commit.setStyleSheet(style)
                nom_commit.mousePressEvent = self.commitMousePress
                self.nom_commits.addWidget(nom_commit)
                author_name:QLabel = QLabel(com.author.name)
                author_name.setFixedHeight(GitLog.lineHeight)
                author_name.setStyleSheet(style)
                author_name.mousePressEvent = self.commitMousePress
                self.nom_authors.addWidget(author_name)
                hex:QLabel = QLabel(com.hexsha)
                hex.setFixedHeight(GitLog.lineHeight)
                hex.setStyleSheet(style)
                hex.mousePressEvent = self.commitMousePress
                self.id_commits.addWidget(hex)

                self.row[y] = [com.hexsha,wid,nom_commit,author_name,hex]
                self.row[com.hexsha] = [y,wid,nom_commit,author_name,hex]
                y+=1

        self.cercle:self.Cercles = self.Cercles(self)
        self.view.addLayout(self.nom_heads)
        self.view.addWidget(self.cercle)
        self.view.addLayout(self.nom_commits)
        self.view.addLayout(self.nom_authors)
        self.view.addLayout(self.id_commits)

    def contextMenuEvent(self, event):
        if len(repo().index.diff(None)) == 0:
            contextMenu:QMenu = QMenu(self)
            
            checkouts:list[QAction] = []
            checkout:QMenu = contextMenu.addMenu("Checkout")
            checkout_commit:QAction = checkout.addAction("this commit")
            for i in range(len(self.columns)):
                if self.selected == self.branchs_commits[i][0].hexsha and self.columns[i].name != "HEAD" and self.columns[i] in repo().branches:
                    checkouts.append(checkout.addAction(self.columns[i].name))
            
            merges:list[QAction] = []
            merge:QMenu = contextMenu.addMenu("Merge")
            for i in range(len(self.columns)):
                if self.selected == self.branchs_commits[i][0].hexsha and self.columns[i].name != "HEAD" and self.columns[i] in repo().branches:
                    merges.append(merge.addAction(self.columns[i].name))
            
            action:QAction = contextMenu.exec_(self.mapToGlobal(event.pos()))
            w:QMainWindow = window()
            if action == checkout_commit:
                repo().git.checkout(self.selected)
                w.Refresh()
            if action in checkouts:
                repo().git.checkout(action.text())
                w.Refresh()
            if action in merges:
                try:
                    repo().git.merge(action.text())
                except Exception:
                    pass
                w.Refresh()
        else:
            contextMenu:QMenu = QMenu(self)
            contextMenu.addAction("Changes not staged")
            contextMenu.exec_(self.mapToGlobal(event.pos()))


    def commitMousePress(self,e:QMouseEvent):
        if self.selected in self.row:
            ele:list[Object] = self.row[self.selected]
            for i in range(1,len(ele)):
                style:str = "border:1px solid black;"
                if self.selected == repo().head.commit.hexsha:
                    style += "background-color: lightgreen;"
                ele[i].setStyleSheet(style)
        self.selected:str = self.row[int((e.globalY()-self.y()+self.verticalScrollBar().value())/GitLog.lineHeight)-1][0]
        ele:list[Object] = self.row[self.selected]
        for i in range(1,len(ele)):
            ele[i].setStyleSheet("border:1px solid black;background-color: cyan;")
        self.cercle.repaint()

    class Cercles(QWidget):
        def __init__(self,log):
            super().__init__()

            self.log:GitLog = log

            self.commit:dict[str,list[Object]] = {}
            y:int = 0
            for com in self.log.repo_commits:
                if not com.hexsha in self.log.commits:
                    i:int = 0
                    for e in range(len(self.log.columns)):
                        if com in self.log.branchs_commits[e]:
                            i = e
                            break
                    self.commit[com.hexsha] = [com,y,QPoint(i*GitLog.lineHeight/2+GitLog.lineHeight/4,y*GitLog.lineHeight+GitLog.lineHeight/2)]
                    y += 1

        def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
            for com in self.commit:
                commit:list[Object] = self.commit[com]
                commit[2] = QPoint(commit[2].x(),commit[1]*GitLog.lineHeight+GitLog.lineHeight/2)
            return super().resizeEvent(a0)

        def paintEvent(self,e):
            qp:QPainter = QPainter(self)
            for com in self.log.repo_commits:
                if not com.hexsha in self.log.commits:
                    a:bool = False
                    if com.hexsha == self.log.selected:
                        a=True
                        qp.setBrush(QBrush(Qt.cyan))
                    elif com.hexsha == repo().head.commit.hexsha:
                        a=True
                        qp.setBrush(QBrush(Qt.green))
                    qp.drawEllipse(self.commit[com.hexsha][2].x()-GitLog.lineHeight/4,self.commit[com.hexsha][2].y()-GitLog.lineHeight/4,GitLog.lineHeight/2,GitLog.lineHeight/2)
                    if a:
                        qp.setBrush(QBrush())
                for parent in com.parents:
                    qp.drawLine(self.commit[com.hexsha][2].x(),self.commit[com.hexsha][2].y(),
                        self.commit[parent.hexsha][2].x(),self.commit[parent.hexsha][2].y())
            qp.end()