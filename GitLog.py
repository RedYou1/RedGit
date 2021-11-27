from datetime import date, datetime
from PyQt5 import QtGui
from Global import *

class GitLog(QScrollArea):

    lineHeight:int = 30

    def __init__(self):
        super().__init__()

        self.selected:str = ""

        self.repo_commits:list[Commit] = list(Setting.repo.iter_commits(all=True))

        self.view:QHBoxLayout = QHBoxLayout()

        self.branchs:list[Reference] = Setting.repo.refs
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
        if Setting.repo.head.is_detached:
            temp.append(Setting.repo.head)

        temp2:list[Tuple[datetime,list[Commit]]] = []
        for b in self.branchs:
            temp2.append((b.commit.committed_datetime,b))
        def takeFirst(ele):
            return ele[0]
        temp2.sort(key=takeFirst,reverse=True)
        for branch in temp2:
            self.columns.append(branch[1])
            self.branchs_commits.append(list(Setting.repo.iter_commits(rev=branch[1],first_parent=True)))

        self.row:dict[Union[int,str],list[Object]] = {}

        max:int = 0
        y:int = 0
        for com in self.repo_commits:
            if not com.hexsha in self.commits:

                temp:QHBoxLayout = QHBoxLayout()
                for i in range(len(self.columns)):
                    if com == self.branchs_commits[i][0]:
                        t:QLabel = QLabel(self.columns[i].name)
                        if (Setting.repo.head.is_detached and self.columns[i].name == "HEAD") or \
                            (not Setting.repo.head.is_detached and self.columns[i] == Setting.repo.head.ref):
                            t.setObjectName("HeadSelected")
                        else:
                            t.setObjectName("Head")
                        temp.addWidget(t)
                wid:QWidget = QWidget()
                wid.setLayout(temp)
                wid.setFixedHeight(GitLog.lineHeight)
                wid.mousePressEvent = self.commitMousePress
                self.nom_heads.addWidget(wid)
                temp:int = temp.count()
                if max < temp:
                    max:int = temp
                nom_commit:QLabel = QLabel(com.message.split('\n')[0])
                nom_commit.setFixedHeight(GitLog.lineHeight)
                nom_commit.mousePressEvent = self.commitMousePress
                self.nom_commits.addWidget(nom_commit)
                author_name:QLabel = QLabel(com.author.name)
                author_name.setFixedHeight(GitLog.lineHeight)
                author_name.mousePressEvent = self.commitMousePress
                self.nom_authors.addWidget(author_name)
                hex:QLabel = QLabel(com.hexsha)
                hex.setFixedHeight(GitLog.lineHeight)
                hex.mousePressEvent = self.commitMousePress
                self.id_commits.addWidget(hex)

                if com.hexsha == self.selected:
                    wid.setObjectName("commitSelected")
                    nom_commit.setObjectName("commitSelected")
                    author_name.setObjectName("commitSelected")
                    hex.setObjectName("commitSelected")
                elif com.hexsha == Setting.repo.head.commit.hexsha:
                    wid.setObjectName("commitHead")
                    nom_commit.setObjectName("commitHead")
                    author_name.setObjectName("commitHead")
                    hex.setObjectName("commitHead")
                else:
                    wid.setObjectName("commit")
                    nom_commit.setObjectName("commit")
                    author_name.setObjectName("commit")
                    hex.setObjectName("commit")

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
        if len(Setting.repo.index.diff(None)) == 0:
            contextMenu:QMenu = QMenu(self)
            
            checkouts:list[QAction] = []
            checkout:QMenu = contextMenu.addMenu("Checkout")
            checkout_commit:QAction = checkout.addAction("this commit")
            for i in range(len(self.columns)):
                if self.selected == self.branchs_commits[i][0].hexsha and self.columns[i].name != "HEAD" and self.columns[i] in Setting.repo.branches:
                    checkouts.append(checkout.addAction(self.columns[i].name))
            
            createBranch:QAction = contextMenu.addAction("Create Branch")

            delBranchs:list[str] = []
            for b in Setting.repo.branches:
                if b.is_detached and b.commit.hexsha == self.selected:
                    delBranchs.append(b.name)

            delBranchActs:list[QAction] = []
            if len(delBranchs) > 0:
                delBranch:QMenu = contextMenu.addMenu("Delete Branch")
                for a in delBranchs:
                    delBranchActs.append(delBranch.addAction(a))

            merge:QAction = contextMenu.addAction("Merge")
            
            pushs:list[QAction] = []
            if not Setting.repo.head.is_detached and self.selected == Setting.repo.active_branch.commit.hexsha:
                lenOfRemotes:int = len(Setting.repo.remotes)
                if lenOfRemotes > 0:
                    push:QMenu = contextMenu.addMenu("Pushes")
                    for remote in Setting.repo.remotes:
                        pushs.append(push.addAction(remote.name))

            pulls:list[QAction] = []
            if not Setting.repo.head.is_detached:
                lenOfRemotes:int = len(Setting.repo.remotes)
                if lenOfRemotes > 0:
                    push:QMenu = contextMenu.addMenu("Pulls")
                    for remote in Setting.repo.remotes:
                        r:QMenu = push.addMenu(remote.name)
                        for branch in remote.refs:
                            if branch.is_detached and branch.commit.hexsha == self.selected:
                                pulls.append(r.addAction(branch.name.split('/')[1]))

            action:QAction = contextMenu.exec_(self.mapToGlobal(event.pos()))
            if action == checkout_commit:
                Setting.repo.git.checkout(self.selected)
                Setting.window.Refresh()
            if action == createBranch:
                self.msg:QWidget = QWidget()
                self.msg.setWindowTitle("Create Branch")
                v:QVBoxLayout = QVBoxLayout() 
                v.addWidget(QLabel("Name of the new branch:"))
                self.newBranchName:QLineEdit = QLineEdit()
                v.addWidget(self.newBranchName)
                h:QHBoxLayout = QHBoxLayout()
                cancel:QPushButton = QPushButton()
                cancel.setText("Cancel")
                cancel.setCheckable(True)
                cancel.clicked.connect(self.msg.close)
                h.addWidget(cancel)
                create:QPushButton = QPushButton()
                create.setText("Create")
                create.setCheckable(True)
                create.clicked.connect(self.createNewBranch)
                h.addWidget(create)
                v.addLayout(h)
                self.msg.setLayout(v)
                self.msg.show()
            if action in delBranchActs:
                if not Setting.repo.head.is_detached and action.text() == Setting.repo.active_branch.name:
                    Setting.repo.git.checkout(Setting.repo.head.commit.hexsha)
                Setting.repo.git.branch(action.text(),D=True)
                Setting.window.Refresh()
            if action in checkouts:
                Setting.repo.git.checkout(action.text())
                Setting.window.Refresh()
            if action == merge:
                try:
                    Setting.repo.git.merge(self.selected)
                except Exception:
                    pass
                Setting.window.Refresh()
            
            if action in pushs:
                Setting.repo.git.push(action.text(),Setting.repo.active_branch.name)
                Setting.window.Refresh()

            if action in pulls:
                try:
                    Setting.repo.git.pull(action.parent().title(),action.text())
                except Exception:
                    pass
                Setting.window.Refresh()
        else:
            contextMenu:QMenu = QMenu(self)
            contextMenu.addAction("Changes not staged")
            contextMenu.exec_(self.mapToGlobal(event.pos()))

    def createNewBranch(self,e):
        if len(self.newBranchName.text()) > 0:
            Setting.repo.git.checkout(self.selected)
            Setting.repo.git.branch(self.newBranchName.text())
            Setting.repo.git.checkout(self.newBranchName.text())
            self.msg.close()
            Setting.window.Refresh()


    def commitMousePress(self,e:QMouseEvent):
        if self.selected in self.row:
            ele:list[Object] = self.row[self.selected]
            for i in range(1,len(ele)):
                if self.selected == Setting.repo.head.commit.hexsha:
                    ele[i].setStyleSheet("commitHead")
                else:
                    ele[i].setStyleSheet("commit")
                ele[i].repaint()
        self.selected:str = self.row[int((e.globalY()-self.y()+self.verticalScrollBar().value())/GitLog.lineHeight)-1][0]
        ele:list[Object] = self.row[self.selected]
        for i in range(1,len(ele)):
            ele[i].setStyleSheet("commitSelected")
            ele[i].repaint()
        self.cercle.repaint()

    class Cercles(QWidget):
        def __init__(self,log):
            super().__init__()

            self.log:GitLog = log

            self.commit:dict[str,list[Object]] = {}
            y:int = 0
            maxi:int = 0
            for com in self.log.repo_commits:
                if not com.hexsha in self.log.commits:
                    i:int = 0
                    for e in range(len(self.log.columns)):
                        if com in self.log.branchs_commits[e]:
                            i = e
                            break
                    if i > maxi:
                        maxi = i
                    self.commit[com.hexsha] = [com,y,QPoint(i*GitLog.lineHeight+GitLog.lineHeight/2,y*GitLog.lineHeight+GitLog.lineHeight/2)]
                    y += 1
            
            self.setFixedWidth((maxi+1)*GitLog.lineHeight)
            self.setFixedHeight(len(self.log.repo_commits)*GitLog.lineHeight)

        def paintEvent(self,e):
            qp:QPainter = QPainter(self)
            for com in self.log.repo_commits:
                if not com.hexsha in self.log.commits:
                    a:bool = False
                    if com.hexsha == self.log.selected:
                        a=True
                        qp.setBrush(QBrush(Qt.cyan))
                    elif com.hexsha == Setting.repo.head.commit.hexsha:
                        a=True
                        qp.setBrush(QBrush(Qt.green))
                    qp.drawEllipse(self.commit[com.hexsha][2].x()-GitLog.lineHeight/4,self.commit[com.hexsha][2].y()-GitLog.lineHeight/4,GitLog.lineHeight/2,GitLog.lineHeight/2)
                    if a:
                        qp.setBrush(QBrush())
                for parent in com.parents:
                    x1 = self.commit[parent.hexsha][2].x()
                    y1 = self.commit[parent.hexsha][2].y()
                    x2 = self.commit[com.hexsha][2].x()
                    y2 = self.commit[com.hexsha][2].y()

                    if x1 < x2:
                        qp.drawLine(x1,y1,x2-GitLog.lineHeight/2,y1)
                        qp.drawLine(x2,y1-GitLog.lineHeight/2,x2,y2)
                        qp.drawArc(x2-GitLog.lineHeight,y1-GitLog.lineHeight,
                            GitLog.lineHeight,GitLog.lineHeight,
                            270*16,90*16)
                    elif x1 > x2:
                        qp.drawLine(x1,y1,x2+GitLog.lineHeight/2,y1)
                        qp.drawLine(x2,y2,x2,y1-GitLog.lineHeight/2)
                        qp.drawArc(x2,y1-GitLog.lineHeight,
                            GitLog.lineHeight,GitLog.lineHeight,
                            270*16,-90*16)
                    else:
                        qp.drawLine(x1,y1,x2,y2)

            qp.end()