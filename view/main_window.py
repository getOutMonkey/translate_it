# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
# from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot
import sys
import os

from ui_views.mainWindow import *

# для теста, потом убрать
# ===========================================================
a = r'Однажды весною, в час небывало жаркого заката, в Москве, на Патриарших прудах, появились два гражданина.'
b = r'Первый был не кто иной, как Михаил Александрович Берлиоз, председатель правления одной из крупнейших московских' \
    r' литературных ассоциаций, сокращенно именуемой МАССОЛИТ, и редактор толстого художественного журнала, а молодой' \
    r' спутник его – поэт Иван Николаевич Понырев, пишущий под псевдонимом Бездомный.'
c = ''
ao = 'The plot of the story is rather simple. Two people, a young one and an old one, lived together. The young' \
     ' man helped the old man to keep the house. But with time the old man started to irritate the young. It was his' \
     ' pale blue eye that made him mad.  What happpened in the end you will know when you read the story.'
bo = 'Now this is the point. You think I am mad. But you should see me. You should see how wisely I started to' \
     ' prepare for the work! I had been very kind to the old man during the whole week before. And every night, about' \
     ' midnight, I opened his door— oh, so quietly! And then I put a dark lantern into the opening, all closed,' \
     ' closed, so that no light shone out. And then I put in my head. Oh, you would laugh to see how carefully I put' \
     ' my head in! I moved it slowly —very, very slowly so that I would not disturb the old man’s sleep.'
co = 'On the eighth night I was more than usually careful in opening the door. I did it so slowly that a clock minute' \
     ' hand moved more quickly than did mine. And I could not hide my feelings of triumph. Just imagine that I was' \
     ' opening the door, little by little, and he didn’t even dream of my secret thoughts. I laughed at the idea; and' \
     ' perhaps he heard me; for he moved on the bed suddenly. You may think that I got out — but no. It was very' \
     ' dark in his room, for the shutters were closed, and so I knew that he could not see me, and I kept opening the' \
     ' door on little by little.'

orig = [ao, bo, co, ao, bo, co, ao, bo, co, c, c, c, c, c, c]
transl = [a, b, a, b, a, b, a, b, c, a, b, c, a, b, c]
tup = list(zip(orig, transl))
print(tup)


# =============================================================


# TODO: класс для обмена информацией с внешними модулями
class MainCommunicate(QtCore.QObject):
    """
    Communicate - пользовательские связи слот-сигнал с MainWindows
    """

    _sig_getblocks = QtCore.pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.file_path = None

    def get_blocks(self, data):
        self._sig_getblocks.emit(data)

    @QtCore.pyqtSlot(str)
    def set_file_path(self, file_path):
        self.file_path = file_path
        # return file_path


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """ Главное окно.
        Ui_MainWindow - форма для setupUi"""
    _current_block = None

    # TODO: реализация сигналов во внешние модули, данные передаются с учетом типа данных
    # Сигнал передающий блоки для загрузки в БД в формате ((original_data, translate_data))
    _sig_setblocks = QtCore.pyqtSignal(tuple)
    # Сигнал передающий путь к файлу при создании проекта
    _sig_setfile_path = QtCore.pyqtSignal(str)

    def __init__(self, controller=None, model=None, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.controller = controller
        self.model = model
        self.setupUi(self)

        self.originalListWidget.itemClicked.connect(self.original_list_click)
        self.translatedListWidget.itemClicked.connect(self.translated_list_click)

        self.originalListWidget.verticalScrollBar().valueChanged.connect(self.sync_translated_scroll)
        self.translatedListWidget.verticalScrollBar().valueChanged.connect(self.sync_original_scroll)

        self.workWithBlockPushButton.clicked.connect(self.work_with_block)
        self.saveBlockPushButton.clicked.connect(self.save_block)
        self.createToolButton.clicked.connect(self.create_new_project)

        self.partner = MainCommunicate()
        self._sig_setfile_path.connect(self.partner.set_file_path)
        self.thread = QtCore.QThread()
        self.partner.moveToThread(self.thread)
        self.thread.start()

        self.on_start()

    def sync_translated_scroll(self, value):
        self.translatedListWidget.verticalScrollBar().setValue(value)

    def sync_original_scroll(self, value):
        self.originalListWidget.verticalScrollBar().setValue(value)

    # TODO: добавить сохранение при смене блока без нажатия кнопки "сохранить"/либо сделать кнопку перевести неактивной
    def work_with_block(self):
        """ Начать работу над переводом выделенного блока текста, срабатывает при нажатии кнопки 'перевести блок'. """
        self._current_block = self.translatedListWidget.currentRow()
        self.translatedPartStackedWidget.setCurrentWidget(self.editorPage)
        self.originalTextEdit.setPlainText(self.originalListWidget.currentItem().text())
        self.translatedTextEdit.setPlainText(self.translatedListWidget.currentItem().text())
        self.workWithBlockPushButton.setEnabled(False)

    def save_block(self):
        """ Сохранение измененного текста блока в item. Срабатывает при нажатии кнопки 'Сохранить блок'. """
        self.translatedListWidget.item(self._current_block).setText(self.translatedTextEdit.toPlainText())
        self.translatedPartStackedWidget.setCurrentWidget(self.listPage)
        self.workWithBlockPushButton.setEnabled(True)

    # TODO: изменить когда будет метод выгрузки из базы
    # TODO: добавил функцию-слот, при необходимости заменить
    # функция-слот, которая со стороны GUI принимает tuple с блоками текста вида ((original_data, translate_data))
    @QtCore.pyqtSlot(tuple)
    def add_text(self, list_of_tuples):
        for o, t in list_of_tuples:
            orig_item = QtWidgets.QListWidgetItem(o, self.originalListWidget)
            trans_item = QtWidgets.QListWidgetItem(t, self.translatedListWidget)
            self.originalListWidget.addItem(orig_item)
            self.translatedListWidget.addItem(trans_item)

    def align_text_blocks_height(self):
        """ Выравнивает высоту блоков текста по большей, срабатывает при изменении размера окна"""
        for string_index in range(self.translatedListWidget.count()):
            orig_index = self.originalListWidget.model().index(string_index)
            transl_index = self.translatedListWidget.model().index(string_index)
            orig_height = self.originalListWidget.visualRect(orig_index).height()
            transl_height = self.translatedListWidget.visualRect(transl_index).height()
            self.originalListWidget.item(string_index).setSizeHint(QtCore.QSize(-1, max(orig_height, transl_height)))
            self.translatedListWidget.item(string_index).setSizeHint(QtCore.QSize(-1, max(orig_height, transl_height)))

    def original_list_click(self):
        """ Синхронизирует выделение блоков текста по клику на блок"""
        self.translatedListWidget.setCurrentRow(self.originalListWidget.currentRow())

    def translated_list_click(self):
        """ Синхронизирует выделение блоков текста по клику на блок"""
        self.originalListWidget.setCurrentRow(self.translatedListWidget.currentRow())

    # TODO: метод для теста, пока нет заливки из базы - потом убрать
    def on_start(self):
        pass
        # self.add_text(tup)

    def resizeEvent(self, event):
        """ Переопределение метода изменения размера окна,
            запускает выравниевание высоты блоков при событии изменения окна"""
        event.accept()
        self.align_text_blocks_height()

    def create_new_project(self):
        file = QtWidgets.QFileDialog.getOpenFileName(
            parent=self, caption='Новый проект', filter='All (*);;TXT (*.txt)', initialFilter='TXT (*.txt)'
        )
        # путь к файлу который нужно прочитать
        file_path = os.path.abspath(file[0])
        if file_path:
            self._sig_setfile_path.emit(file_path)
            print(self._sig_setfile_path)

    def closeEvent(self, event):
        # диалоговое окно ... подумать где создавать экземпляр
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
