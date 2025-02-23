from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QButtonGroup, QSizePolicy
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from ui_main import Ui_MainWindow
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QPainter
from Signal import my_signal
from function_pyutchemflopy import pyutchemflopy_model
import sys
from resultplot import *


# 该类是为了显示进度条
class SimulationThread(QThread):
    progress_updated = Signal(int)
    simulation_completed = Signal()

    def __init__(self, file_path, parameters):
        super(SimulationThread, self).__init__()
        self.file_path = file_path
        self.parameters = parameters

    def run(self):
        # 模拟开始前的准备工作，例如初始化
        total_steps = 100  # 假设有100步
        self.progress_updated.emit(0)  # 发送零进度信号

        for step in range(total_steps):
            # 模拟每一步
            # 在每步完成后发射信号更新进度条
            progress_percentage = int((step + 1) / total_steps * 100)
            self.progress_updated.emit(progress_percentage)
            self.msleep(100)  # 模拟一些计算耗时

        # 模拟完成后，发射信号通知主线程
        self.simulation_completed.emit()


# 设置图形界面显示
class CustomGraphicsView(QGraphicsView):
    def __init__(self):
        super(CustomGraphicsView, self).__init__()

        # 创建场景
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # 设置视图属性
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 调整大小策略
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(1000, 500)  # 设置最小尺寸，根据需要调整

    def Sn_XY(self, num):
        # 调用 result_plot.py 中的 draw_sn_xy_result 函数
        Sn_XY(num)

    def Sn_XZ(self, num):
        # 调用 result_plot.py 中的 draw_sn_xy_result 函数
        Sn_XZ(num)

    def Sn_YZ(self, num):
        # 调用 result_plot.py 中的 draw_sn_xy_result 函数
        Sn_YZ(num)

    def head_plot(self):
        with open("path_record.txt", 'r') as record_file:
            file_path = record_file.read().strip()
        # 调用 result_plot.py 中的 draw_sn_xy_result 函数
        head_plot(file_path)

    def conc_XY(self, num):
        # 调用 result_plot.py 中的 draw_sn_xy_result 函数
        conc_XY(num, conc)

    def conc_XZ(self, num):
        # 调用 result_plot.py 中的 draw_sn_xy_result 函数
        conc_XZ(num, conc)

    def conc_YZ(self, num):
        # 调用 result_plot.py 中的 draw_sn_xy_result 函数
        conc_YZ(num, conc)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()  # UI类的实例化()
        self.ui.setupUi(self)
        self.bind_signals()  # 绑定信号与槽
        self.ui.stackedWidget.setCurrentIndex(0)  # 初始化界面到第一页

        # 寻找 graphicsView 控件，将其设置为 CustomGraphicsView 的实例
        for child in self.ui.stackedWidget.widget(2).children():
            if isinstance(child, QGraphicsView):
                self.customGraphicsView = CustomGraphicsView()
                self.ui.stackedWidget.widget(2).layout().replaceWidget(child, self.customGraphicsView)
                break

        # 创建 QButtonGroup 来管理结果类型选择
        self.result_type_group = QButtonGroup()
        self.result_type_group.addButton(self.ui.checkBox_1, 1)  # 1 表示饱和度分布
        self.result_type_group.addButton(self.ui.checkBox_2, 2)  # 2 表示水头分布
        self.result_type_group.addButton(self.ui.checkBox_3, 3)  # 3 表示浓度分布

        # 创建 QButtonGroup 来管理视图类型选择
        self.view_type_group = QButtonGroup()
        self.view_type_group.addButton(self.ui.checkBox_4, 4)
        self.view_type_group.addButton(self.ui.checkBox_5, 5)
        self.view_type_group.addButton(self.ui.checkBox_6, 6)

    # 设置信号与槽
    def bind_signals(self):
        # 定义信号，使的界面上的一些操作连接到对应的函数上
        # self.ui.___ACTION___.triggered.connect(___FUNCTION___)
        # self.ui.___BUTTON___.clicked.connect(___FUNCTION___)
        # self.ui.___COMBO_BOX___.currentIndexChanged.connect(___FUNCTION___)
        # self.ui.___SPIN_BOX___.valueChanged.connect(___FUNCTION___)
        # 自定义信号.属性名.connect(___FUNCTION___)

        # 实现功能：点击按钮，切换到对应页面
        self.ui.pushButton_1.clicked.connect(self.display_page1)
        self.ui.pushButton_2.clicked.connect(self.display_page2)
        self.ui.pushButton_3.clicked.connect(self.display_page3)

        # 实现功能：点击浏览，导入模型输入文件，并将文件路径传递给函数
        self.ui.toolButton.clicked.connect(self.open_input)

        # 实现功能：点击开始模拟，运行程序
        self.ui.pushButton_4.clicked.connect(self.start_simulation)

        # 实现功能：显示模拟进度
        my_signal.setProgressBar.connect(self.set_progress_bar)

        # 实现功能：显示指定模拟结果
        self.ui.pushButton_5.clicked.connect(self.resultshow)

    # 实现功能：点击按钮，切换到对应页面
    # 跳转至第一页
    def display_page1(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    # 跳转至第一页
    def display_page2(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    # 跳转至第一页
    def display_page3(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    # 实现功能：点击浏览，导入模型输入文件
    def open_input(self):
        # 打开文件对话框
        file_dialog = QFileDialog()
        # file_dialog.setNameFilter("Text Files (*.txt)")
        # file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setFileMode(QFileDialog.AnyFile)

        if file_dialog.exec_():
            # 获取选中文件的路径
            file_path = file_dialog.selectedFiles()[0]
            # 在lineEdit中显示文件路径
            self.ui.lineEdit.setText(file_path)
            return (file_path)

    # 实现功能：设置模型输入参数,并将参数传递给函数
    def model_parameters(self):
        # 从行编辑框获取文本
        value_1 = self.ui.lineEdit_1.text()  # 孔隙度
        value_2 = self.ui.lineEdit_2.text()  # Q
        value_3 = self.ui.lineEdit_3.text()  # VOF
        value_4 = self.ui.lineEdit_4.text()  # Kx
        value_5 = self.ui.lineEdit_5.text()  # Ky
        value_6 = self.ui.lineEdit_6.text()  # a
        value_7 = self.ui.lineEdit_7.text()  # 液相残余饱和度
        value_8 = self.ui.lineEdit_8.text()  # BC模型参数
        value_9 = self.ui.lineEdit_9.text()  # 饱和溶解度

        # 转换为浮点数

        parameters = [float(value_1), float(value_4), float(value_5), float(value_6), float(value_2),
                      float(value_3), float(value_7), float(value_8), float(value_9)]

        return parameters

    # 实现功能：点击开始模拟，运行程序,显示进度
    def start_simulation(self):
        file_path = self.ui.lineEdit.text()
        # 将斜杠替换为双反斜杠
        file_path = file_path.replace('/', '\\')
        P = self.model_parameters()

        # 创建并启动模拟线程
        self.simulation_thread = SimulationThread(file_path, P)
        self.simulation_thread.progress_updated.connect(self.update_progress)
        self.simulation_thread.simulation_completed.connect(self.show_simulation_completed)
        self.simulation_thread.start()

        pyutchemflopy_model(file_path, P)

    def update_progress(self, percentage):
        self.ui.progressBar.setValue(percentage)

    def show_simulation_completed(self):
        QMessageBox.information(self, "Simulation Completed", "Simulation has been completed.")

    # 实现功能：显示模拟进度
    def set_progress_bar(self, progress: int):
        self.ui.progressBar.setValue(progress)

    # 实现功能：显示指定模拟结果
    def resultshow(self):
        # 获取选中的结果类型和视图类型
        selected_result_id = self.result_type_group.checkedId()             # 确定绘图函数
        selected_view_type = self.view_type_group.checkedId()               # 确定显示截面
        num = int(self.ui.lineEdit_10.text())                               # 确定截面位置

        if selected_result_id == -1 or selected_view_type is None:
            # 用户没有选择任何结果类型或视图类型
            return
        # 根据选项对应的 ID 和视图类型 调用相应的绘图函数
        if selected_result_id == 1:  # 饱和度分布
            if selected_view_type == 4:
                self.customGraphicsView.Sn_XY(num)
            elif selected_view_type == 5:
                self.customGraphicsView.Sn_XZ(num)
            elif selected_view_type == 6:
                self.customGraphicsView.Sn_YZ(num)
        elif selected_result_id == 2:  # 水头分布
            self.view_type_group.button(4).setChecked(True)
            self.ui.lineEdit_10.setText("0")
            self.customGraphicsView.head_plot()
        elif selected_result_id == 3:  # 浓度分布
            if selected_view_type == 4:
                self.customGraphicsView.conc_XY(num)
            if selected_view_type == 5:
                self.customGraphicsView.conc_XZ(num)
            if selected_view_type == 6:
                self.customGraphicsView.conc_YZ(num)

            # 切换到显示结果的页面（假设是 stackedWidget 的第三个页面）
            self.ui.stackedWidget.setCurrentIndex(2)


if __name__ == "__main__":
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec())
