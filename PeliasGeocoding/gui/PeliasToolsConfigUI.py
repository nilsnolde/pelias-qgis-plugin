# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PeliasTools/gui/PeliasToolsConfigUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PeliasToolsDialogConfigBase(object):
    def setupUi(self, PeliasToolsDialogConfigBase):
        PeliasToolsDialogConfigBase.setObjectName("PeliasToolsDialogConfigBase")
        PeliasToolsDialogConfigBase.resize(414, 67)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PeliasToolsDialogConfigBase.sizePolicy().hasHeightForWidth())
        PeliasToolsDialogConfigBase.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(PeliasToolsDialogConfigBase)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.gridLayout.setObjectName("gridLayout")
        self.providers = QtWidgets.QWidget(PeliasToolsDialogConfigBase)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.providers.sizePolicy().hasHeightForWidth())
        self.providers.setSizePolicy(sizePolicy)
        self.providers.setObjectName("providers")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.providers)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout.addWidget(self.providers, 0, 0, 1, 3)
        self.buttonBox = QtWidgets.QDialogButtonBox(PeliasToolsDialogConfigBase)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 2, 1, 1)
        self.provider_add = QtWidgets.QPushButton(PeliasToolsDialogConfigBase)
        self.provider_add.setObjectName("provider_add")
        self.gridLayout.addWidget(self.provider_add, 1, 0, 1, 1)
        self.provider_remove = QtWidgets.QPushButton(PeliasToolsDialogConfigBase)
        self.provider_remove.setObjectName("provider_remove")
        self.gridLayout.addWidget(self.provider_remove, 1, 1, 1, 1)

        self.retranslateUi(PeliasToolsDialogConfigBase)
        QtCore.QMetaObject.connectSlotsByName(PeliasToolsDialogConfigBase)

    def retranslateUi(self, PeliasToolsDialogConfigBase):
        _translate = QtCore.QCoreApplication.translate
        PeliasToolsDialogConfigBase.setWindowTitle(_translate("PeliasToolsDialogConfigBase", "Provider Settings"))
        self.provider_add.setText(_translate("PeliasToolsDialogConfigBase", "Add"))
        self.provider_remove.setText(_translate("PeliasToolsDialogConfigBase", "Remove"))

