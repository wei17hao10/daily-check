import contextlib
import sys
from io import StringIO
from runpy import run_path

from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from UI.python_editor import Ui_Form


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


class PythonEditor:
    def __init__(self):
        self.ui = QWidget()
        self.form = Ui_Form()
        self.form.setupUi(self.ui)

        self.file_path = None
        self.file_type = None

        self.form.btn_execute.clicked.connect(self.execute_python)
        # self.form.btn_new.clicked.connect(self.new)
        self.form.btn_open.clicked.connect(self.open)
        self.form.btn_save.clicked.connect(self.save)
        self.form.btn_close.clicked.connect(self.close)

    def execute_python(self):
        self.save()
        if not isinstance(self.file_path, str):
            return

        with stdoutIO() as s:
            try:
                run_path(path_name=self.file_path)
            except Exception as e:
                print(f'Error ===> {e}')
        self.form.tb_result.setText(s.getvalue())

    def open(self):
        self.file_path, self.file_type = QFileDialog.getOpenFileName(self.ui,
                                                                     "Open File",
                                                                     "./",
                                                                     "Python (*.py);;Txt (*.txt)")
        if self.file_path:
            file = open(self.file_path, 'r')
            file_read = file.read()
            file.close()
            self.form.te_python.setText(file_read)
        self.form.lb_path.setText(self.file_path)

    def save(self):
        code = self.form.te_python.text()
        if self.file_path:
            file = open(self.file_path, 'r')
            file_read = file.read()
            file.close()
            if file_read != code:
                file = open(self.file_path, 'w')
                file.write(code)
                file.close()
            QMessageBox.information(self.ui, "Info", "Python script saved.")
        else:
            self.file_path, _ = QFileDialog.getSaveFileName(self.ui,
                                                            "Save File",
                                                            "./",
                                                            "Python File (*.py);;Text File (*.txt)")
            if self.file_path == '':
                self.file_path = None
            else:
                file = open(self.file_path, 'w')
                file.write(code)
                file.close()
                self.form.lb_path.setText(self.file_path)
            # QMessageBox.information(self.ui, "Info", "Python script saved.")

    def close(self):
        code = self.form.te_python.text()

        if self.file_path:
            file = open(self.file_path, 'r')
            file_read = file.read()
            file.close()
            if file_read != code:
                result = QMessageBox.question(self.ui,
                                              "Save or not",
                                              "Do you want to save the script?",
                                              QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                if result == QMessageBox.Yes:
                    file = open(self.file_path, 'w')
                    file.write(code)
                    file.close()
                    QMessageBox.information(self.ui, "Info", "Python script saved.")
                    self.form.te_python.clear()
                elif result == QMessageBox.No:
                    self.form.te_python.clear()
                elif result == QMessageBox.Cancel:
                    pass
            else:
                self.form.te_python.clear()
        else:
            if len(code.strip()) == 0:
                return
            else:
                result = QMessageBox.question(self.ui,
                                              "Save or not",
                                              "Do you want to save the script?",
                                              QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                if result == QMessageBox.Yes:
                    self.save()
                    self.form.te_python.clear()
                elif result == QMessageBox.No:
                    self.form.te_python.clear()
                elif result == QMessageBox.Cancel:
                    pass
        self.file_path = None
        self.form.lb_path.setText("unsaved file (can not be executed)")
