from __future__ import annotations
import os
import sys
from typing import List, Set
from PyQt5 import QtCore, QtGui, QtWidgets


class DNSRazzleGUI(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DNSRazzle GUI")
        self.resize(700, 500)
        self.screenshot_window: QtWidgets.QScrollArea | None = None
        self.screenshot_layout: QtWidgets.QVBoxLayout | None = None
        self.screenshot_images: List[QtGui.QPixmap] = []
        self.displayed_files: Set[str] = set()
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.readyReadStandardError.connect(self._read_output)
        self.process.finished.connect(lambda *_: self.status_label.setText("Done"))
        self._create_widgets()

    def _create_widgets(self) -> None:
        form = QtWidgets.QFormLayout()
        self.domain_edit = QtWidgets.QLineEdit()
        form.addRow("Domain(s)", self.domain_edit)

        self.file_edit = QtWidgets.QLineEdit()
        browse_file = QtWidgets.QPushButton("Browse")
        browse_file.clicked.connect(self.browse_file)
        file_layout = QtWidgets.QHBoxLayout()
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse_file)
        form.addRow("Domain list file", file_layout)

        self.out_edit = QtWidgets.QLineEdit()
        browse_out = QtWidgets.QPushButton("Browse")
        browse_out.clicked.connect(self.browse_out)
        out_layout = QtWidgets.QHBoxLayout()
        out_layout.addWidget(self.out_edit)
        out_layout.addWidget(browse_out)
        form.addRow("Output directory", out_layout)

        self.browser_combo = QtWidgets.QComboBox()
        self.browser_combo.addItems(["chrome", "firefox"])
        form.addRow("Browser", self.browser_combo)

        self.threads_edit = QtWidgets.QLineEdit("10")
        form.addRow("Threads", self.threads_edit)

        self.delay_edit = QtWidgets.QLineEdit("2")
        form.addRow("Screenshot delay", self.delay_edit)

        self.nmap_check = QtWidgets.QCheckBox("Run nmap")
        self.recon_check = QtWidgets.QCheckBox("Run dnsrecon")
        self.noss_check = QtWidgets.QCheckBox("No screenshots")
        self.generate_check = QtWidgets.QCheckBox("Generate only")
        self.debug_check = QtWidgets.QCheckBox("Debug")
        checks = QtWidgets.QGridLayout()
        checks.addWidget(self.nmap_check, 0, 0)
        checks.addWidget(self.recon_check, 0, 1)
        checks.addWidget(self.noss_check, 1, 0)
        checks.addWidget(self.generate_check, 1, 1)
        checks.addWidget(self.debug_check, 2, 0)
        form.addRow(checks)

        self.run_button = QtWidgets.QPushButton("Run")
        self.run_button.clicked.connect(self.run_dnsrazzle)
        self.status_label = QtWidgets.QLabel("Idle")
        run_layout = QtWidgets.QHBoxLayout()
        run_layout.addWidget(self.run_button)
        run_layout.addWidget(self.status_label)
        form.addRow(run_layout)

        self.output_text = QtWidgets.QPlainTextEdit()
        self.output_text.setReadOnly(True)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form)
        main_layout.addWidget(self.output_text)

    def browse_file(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select file")
        if path:
            self.file_edit.setText(path)

    def browse_out(self) -> None:
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select directory")
        if path:
            self.out_edit.setText(path)

    def show_screenshot_window(self) -> None:
        if self.screenshot_window and self.screenshot_window.isVisible():
            return
        self.screenshot_window = QtWidgets.QScrollArea()
        self.screenshot_window.setWindowTitle("Screenshots")
        container = QtWidgets.QWidget()
        self.screenshot_layout = QtWidgets.QVBoxLayout(container)
        self.screenshot_window.setWidget(container)
        self.screenshot_window.setWidgetResizable(True)
        self.screenshot_window.show()
        QtCore.QTimer.singleShot(1000, self.update_screenshots)

    def update_screenshots(self) -> None:
        if not (self.screenshot_window and self.screenshot_window.isVisible()):
            return
        ss_dir = os.path.join(self.out_edit.text(), "screenshots")
        if os.path.isdir(ss_dir):
            for fname in sorted(os.listdir(ss_dir)):
                if fname.endswith(".png") and fname not in self.displayed_files:
                    path = os.path.join(ss_dir, fname)
                    pix = QtGui.QPixmap(path)
                    if not pix.isNull():
                        lbl = QtWidgets.QLabel()
                        lbl.setPixmap(pix)
                        lbl.setAlignment(QtCore.Qt.AlignHCenter)
                        lbl.setToolTip(fname)
                        self.screenshot_layout.addWidget(lbl)
                        self.screenshot_images.append(pix)
                        self.displayed_files.add(fname)
        QtCore.QTimer.singleShot(2000, self.update_screenshots)

    def _read_output(self) -> None:
        data = self.process.readAllStandardOutput().data().decode()
        if data:
            self.output_text.appendPlainText(data)
            self.output_text.verticalScrollBar().setValue(self.output_text.verticalScrollBar().maximum())

    def run_dnsrazzle(self) -> None:
        args = [sys.executable, "-u", os.path.join(os.path.dirname(__file__), "DNSrazzle.py")]
        if self.domain_edit.text():
            args += ["-d", self.domain_edit.text()]
        if self.file_edit.text():
            args += ["-f", self.file_edit.text()]
        if self.out_edit.text():
            args += ["-o", self.out_edit.text()]
        if self.browser_combo.currentText() != "chrome":
            args += ["--browser", self.browser_combo.currentText()]
        if self.threads_edit.text():
            args += ["-t", self.threads_edit.text()]
        if self.delay_edit.text():
            args += ["--screenshot-delay", self.delay_edit.text()]
        if self.nmap_check.isChecked():
            args += ["-n"]
        if self.recon_check.isChecked():
            args += ["-r"]
        if self.noss_check.isChecked():
            args += ["--noss"]
        if self.generate_check.isChecked():
            args += ["-g"]
        if self.debug_check.isChecked():
            args += ["--debug"]

        if not self.domain_edit.text() and not self.file_edit.text():
            QtWidgets.QMessageBox.critical(self, "Error", "Please enter a domain or select a file")
            self.status_label.setText("Idle")
            return

        self.status_label.setText("Running...")
        self.show_screenshot_window()
        self.output_text.clear()
        self.process.start(args[0], args[1:])

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.process.state() == QtCore.QProcess.Running:
            self.process.kill()
        event.accept()


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    gui = DNSRazzleGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
