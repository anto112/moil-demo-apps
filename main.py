from model import *


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = model()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
