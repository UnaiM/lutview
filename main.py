import argparse
import functools
import pathlib
import sys

from PySide6 import QtWidgets
import PyOpenColorIO as ocio

import lutview


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('LutView')
        toolbar = self.addToolBar('toolbar')
        style = self.style()
        toolbar.addAction(style.standardIcon(QtWidgets.QStyle.SP_DialogOpenButton),
                          'Open LUT file...', self.open_dialog)
        self.view = lutview.CubeView()
        self.setCentralWidget(self.view)

    @functools.cached_property
    def lut_format_filters(self):
        extensions = []
        result = ['All files (*.*)']
        for pretty, *exts in ocio.FileTransform.getFormats():
            exts = [f'*.{x}' for x in exts]
            extensions += exts
            result.append(f'{pretty} ({" ".join(exts)})')
        result.insert(1, f'All LUT files ({" ".join(sorted(extensions))})')
        return result
    
    @functools.cached_property
    def raw_config(self):
        return ocio.Config.CreateRaw()

    def open_dialog(self):
        lut_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open LUT File', '', ';;'.join(self.lut_format_filters),
            self.lut_format_filters[1])
        if lut_path:
            self._open_lut(pathlib.Path(lut_path))

    def open_lut(self, lut_path):
        lut_path = pathlib.Path(lut_path)
        if not lut_path.exists():
            QtWidgets.QMessageBox.warning(self, 'LutView', f'File not found:\n{lut_path}')
    
    def _open_lut(self, lut_path):
        file_xfm = ocio.FileTransform(str(lut_path))
        try:
            processor = self.raw_config.getProcessor(file_xfm)
        except ocio.Exception as exc:
            QtWidgets.QMessageBox.warning(self, 'LutView', str(exc))
        self.view.load(processor)


def main(lut_path: pathlib.Path | str | None = None) -> int:
    """Show a graphical representation of the colour transform encoded in a LUT file.

    Arguments:
        lut_path: Path to the LUT file to load (optional).

    Returns:
        Qt application return code.
    """
    app = QtWidgets.QApplication()
    window = MainWindow()
    window.show()
    if lut_path:
        window.open_lut(lut_path)
    return(app.exec())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show a graphical representation of the colour '
                                     'transform encoded in a LUT file.')
    parser.add_argument('LUT_PATH', nargs='?', help='Path to the LUT file to load (optional).')
    args = parser.parse_args()
    sys.exit(main(args.LUT_PATH))
