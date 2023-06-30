import contextlib
import sys
from io import StringIO

from PyQt5.QtWidgets import QWidget
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
        self.form.btn_execute.clicked.connect(self.execute_python)

    def execute_python(self):
        code = self.form.te_python.text()
        with stdoutIO() as s:
            try:
                exec(code)
            except Exception as e:
                print(f'Error: {e}')
        self.form.tb_result.setText(s.getvalue())
