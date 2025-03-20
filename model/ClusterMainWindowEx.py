import sys

from PyQt6.QtWidgets import QTableWidgetItem, QMainWindow

from PracticeMl_mid.model.ClusterMainWindow import Ui_MainWindow
from PracticeMl_mid.model.trainmodel import cluster_model




class ClusterMainWindowEx(Ui_MainWindow):
        def setupUi(self, MainWindow):
            super().setupUi(MainWindow)
            # Kết nối nút pushButtonPickSQLite với phương thức xử lý
            self.pushButtonPickSQLite.clicked.connect(self.handleClusterButton)

        def handleClusterButton(self):
            # Gọi hàm cluster_model để lấy DataFrame
            df = cluster_model()
            if df is None:
                print("Failed to retrieve clustering data!")
                return

            # Hiển thị DataFrame lên tableWidget
            self.displayDataFrame(df)

        def displayDataFrame(self, df):
            # Chỉ lấy các cột cần hiển thị
            display_df = df[['customer_id', 'cluster', 'genre_diversity']]

            # Đặt số hàng và cột cho tableWidget
            self.tableWidget.setRowCount(display_df.shape[0])
            self.tableWidget.setColumnCount(display_df.shape[1])

            # Đặt tiêu đề cột
            self.tableWidget.setHorizontalHeaderLabels(display_df.columns.tolist())

            # Điền dữ liệu vào tableWidget
            for i in range(display_df.shape[0]):
                for j in range(display_df.shape[1]):
                    item = QTableWidgetItem(str(display_df.iloc[i, j]))
                    self.tableWidget.setItem(i, j, item)

            # In kết quả ra console (theo yêu cầu)
            print(display_df)


if __name__ == "__main__":
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        MainWindow = QMainWindow()
        ui = ClusterMainWindowEx()
        ui.setupUi(MainWindow)
        MainWindow.show()
        sys.exit(app.exec())

