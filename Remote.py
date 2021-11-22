from os import name
import re
from PyQt5 import QtGui
import git
from git.remote import Remote
from Global import *

class RemoteLayout(QVBoxLayout):
    def __init__(self,main):
        super().__init__()

        buts:QHBoxLayout = QHBoxLayout()

        retour:QPushButton = QPushButton()
        retour.setText("Retour")
        retour.setCheckable(True)
        retour.clicked.connect(main.SetMain)
        buts.addWidget(retour)

        actu:QPushButton = QPushButton()
        actu.setText("Actualiser")
        actu.setCheckable(True)
        actu.clicked.connect(main.actuBut)
        buts.addWidget(actu)

        self.addLayout(buts)

        for remote in repo().remotes:
            self.addLayout(self.GitRemote(remote))
        
        add:QPushButton = QPushButton()
        add.setText("Add")
        add.setCheckable(True)
        add.clicked.connect(self.add)
        self.addWidget(add)

    class GitRemote(QHBoxLayout):
        def __init__(self,remote:Remote):
            super().__init__()
            self.remote:Remote = remote
            self.addWidget(QLabel(remote.name))
            urls:QVBoxLayout = QVBoxLayout()
            for url in remote.urls:
                urls.addWidget(QLabel(url))
            self.addLayout(urls)

            edit:QPushButton = QPushButton()
            edit.setText("Edit")
            edit.setCheckable(True)
            edit.clicked.connect(self.edit)
            self.addWidget(edit)

            remove:QPushButton = QPushButton()
            remove.setText("X")
            remove.setCheckable(True)
            remove.clicked.connect(self.remove)
            self.addWidget(remove)
        
        def remove(self,e):
            git.Remote.remove(repo=repo(),name=self.remote.name)
            window().Refresh()

        def edit(self,e):
            self.w:self.GitRemoteEdit = self.GitRemoteEdit(self.remote)
            self.w.show()
    
        class GitRemoteEdit(QWidget):
            def __init__(self,remote:Remote):
                super().__init__()

                self.remote:Remote = remote

                self.urls:list[QLineEdit] = []
                self.name = None
                self.setWindowTitle("Edit Remote")
                self.Refresh()

            def Refresh(self):
                layout:QVBoxLayout = QVBoxLayout()

                layout2:QHBoxLayout = QHBoxLayout()

                if self.name == None:
                    if self.remote != None:
                        self.name:QLineEdit = QLineEdit(self.remote.name)
                    else:
                        self.name:QLineEdit = QLineEdit()
                layout2.addWidget(self.name)

                
                urls:QVBoxLayout = QVBoxLayout()
                if len(self.urls) == 0:
                    if self.remote != None:
                        for url in self.remote.urls:
                            u:QLineEdit = QLineEdit(url)
                            self.urls.append(u)

                            b:QPushButton = QPushButton()
                            b.setText("X")
                            b.setCheckable(True)
                            b.info = u
                            b.clicked.connect(self.remove)

                            t:QHBoxLayout = QHBoxLayout()
                            t.addWidget(u)
                            t.addWidget(b)
                            urls.addLayout(t)
                    else:
                        u:QLineEdit = QLineEdit()
                        self.urls.append(u)

                        b:QPushButton = QPushButton()
                        b.setText("X")
                        b.setCheckable(True)
                        b.info = u
                        b.clicked.connect(self.remove)

                        t:QHBoxLayout = QHBoxLayout()
                        t.addWidget(u)
                        t.addWidget(b)
                        urls.addLayout(t)
                else:
                    turls:list[QLineEdit] = []
                    for url in self.urls:
                        u:QLineEdit = QLineEdit(url.text())
                        turls.append(u)

                        b:QPushButton = QPushButton()
                        b.setText("X")
                        b.setCheckable(True)
                        b.info = u
                        b.clicked.connect(self.remove)

                        t:QHBoxLayout = QHBoxLayout()
                        t.addWidget(u)
                        t.addWidget(b)
                        urls.addLayout(t)
                    self.urls = turls
                

                layout2.addLayout(urls)
                layout.addLayout(layout2)

                add:QPushButton = QPushButton()
                add.setText("Add")
                add.setCheckable(True)
                add.clicked.connect(self.add)
                layout.addWidget(add)

                h:QHBoxLayout = QHBoxLayout()
                cancel:QPushButton = QPushButton()
                cancel.setText("Cancel")
                cancel.setCheckable(True)
                cancel.clicked.connect(self.close)
                h.addWidget(cancel)

                validate:QPushButton = QPushButton()
                validate.setText("Validate")
                validate.setCheckable(True)
                validate.clicked.connect(self.validate)
                h.addWidget(validate)
                layout.addLayout(h)

                if self.layout():
                    QWidget().setLayout(self.layout())
                self.setLayout(layout)
            
            def remove(self,e):
                b:QPushButton = self.sender()
                self.urls.remove(b.info)
                self.Refresh()

            def add(self,e):
                self.urls.append(QLineEdit())
                self.Refresh()

            def validate(self,e):
                if len(self.urls) > 0:
                    if self.remote != None:
                        git.Remote.remove(repo=repo(),name=self.remote.name)
                    remote = git.Remote.add(repo=repo(),name=self.name.text(),url=self.urls[0].text())
                    for i in range(1,len(self.urls)):
                        remote.add_url(url=self.urls[i].text())
                    self.close()
                    window().Refresh()

    def add(self,e):
        self.w:self.GitRemote.GitRemoteEdit = self.GitRemote.GitRemoteEdit(None)
        self.w.show()
                


