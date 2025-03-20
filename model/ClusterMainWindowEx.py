import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PyQt6.QtWidgets import QTableWidgetItem, QMainWindow, QApplication, QMessageBox, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt  # Thêm import Qt
from PracticeMl_mid.model.ClusterMainWindow import Ui_MainWindow
from PracticeMl_mid.model.trainmodel import cluster_model


class ClusterMainWindowEx(Ui_MainWindow):
    def __init__(self):
        self.MainWindow = None

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.pushButtonPickSQLite.clicked.connect(self.handleClusterButton)
        self.pushFetchMore.clicked.connect(self.handleFetchMoreButton)
        self.pushButtonShow.clicked.connect(self.handleShowChartButton)

        self.current_offset = 0
        self.rows_per_fetch = 256
        self.total_rows_loaded = 0
        self.full_df = pd.DataFrame()

        if not hasattr(self, 'verticalLayout'):
            print("Error: verticalLayout not found in UI setup!")
        else:
            print("verticalLayout found:", type(self.verticalLayout))

    def handleClusterButton(self):
        print("handleClusterButton called")
        self.current_offset = 0
        self.total_rows_loaded = 0
        self.tableWidget.setRowCount(0)
        self.full_df = pd.DataFrame()

        df = cluster_model(offset=self.current_offset, limit=self.rows_per_fetch)
        if df is None:
            print("Failed to retrieve clustering data!")
            return

        self.displayDataFrame(df)
        self.full_df = df.copy()
        self.current_offset += self.rows_per_fetch
        self.total_rows_loaded = df.shape[0]
        print(f"Initial data loaded: {self.full_df.shape}")

    def handleFetchMoreButton(self):
        print("handleFetchMoreButton called")
        df = cluster_model(offset=self.current_offset, limit=self.rows_per_fetch)
        if df is None or df.empty:
            QMessageBox.information(None, "Info", "No more records to fetch")
            return

        self.appendDataFrame(df)
        self.full_df = pd.concat([self.full_df, df], ignore_index=True)
        self.current_offset += self.rows_per_fetch
        self.total_rows_loaded += df.shape[0]
        print(f"More data loaded, total shape: {self.full_df.shape}")

    def handleShowChartButton(self):
        print("handleShowChartButton called")
        if self.full_df.empty:
            print("No data available to plot! Please load data first.")
            return

        print("Drawing chart...")
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=self.full_df['rentals_per_month'], y=self.full_df['genre_diversity'],
                        hue=self.full_df['cluster'], palette='viridis')
        plt.xlabel('Rentals Per Month')
        plt.ylabel('Genre Diversity')
        plt.title('Customer Clustering based on Film and Inventory Interest')

        chart_path = "temp_chart.png"
        print(f"Saving chart to {chart_path}")
        plt.savefig(chart_path)
        plt.close()
        print(f"Chart saved: {os.path.exists(chart_path)}")

        print("Clearing verticalLayout...")
        while self.verticalLayout.count():
            child = self.verticalLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        print("Creating QLabel...")
        label = QLabel()
        print("Loading pixmap...")
        pixmap = QPixmap(chart_path)
        if pixmap.isNull():
            print(f"Error: Pixmap is null, image at {chart_path} could not be loaded!")
            return
        else:
            print("Pixmap loaded successfully")
            print(f"Original pixmap size: {pixmap.width()}x{pixmap.height()}")

        print("Scaling pixmap...")
        try:
            scaled_pixmap = pixmap.scaled(600, 400, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            print(f"Scaled pixmap size: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
        except Exception as e:
            print(f"Error scaling pixmap: {e}")
            return

        print("Setting pixmap to label...")
        try:
            label.setPixmap(scaled_pixmap)
            print("Pixmap set to label successfully")
        except Exception as e:
            print(f"Error setting pixmap to label: {e}")
            return

        if self.verticalLayout is None:
            print("Error: verticalLayout is None! Check your .ui file.")
            return

        print("verticalLayout type:", type(self.verticalLayout))
        print("verticalLayout parent:", self.verticalLayout.parent())
        print("verticalLayout geometry:", self.verticalLayout.geometry())

        try:
            self.verticalLayout.addWidget(label)
            print("Chart added to verticalLayout")
            self.verticalLayout.update()
            parent_widget = self.verticalLayout.parentWidget()
            if parent_widget:
                print("Parent widget geometry:", parent_widget.geometry())
                parent_widget.setMinimumSize(650, 450)
                parent_widget.update()
        except Exception as e:
            print(f"Error adding widget to verticalLayout: {e}")

        try:
            self.MainWindow.update()
            print("MainWindow updated")
        except Exception as e:
            print(f"Error updating MainWindow: {e}")

        try:
            self.MainWindow.repaint()
            print("MainWindow repainted")
        except Exception as e:
            print(f"Error repainting MainWindow: {e}")

    def displayDataFrame(self, df):
        display_df = df[['customer_id', 'cluster', 'genre_diversity']]
        self.tableWidget.setRowCount(display_df.shape[0])
        self.tableWidget.setColumnCount(display_df.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(display_df.columns.tolist())
        for i in range(display_df.shape[0]):
            for j in range(display_df.shape[1]):
                item = QTableWidgetItem(str(display_df.iloc[i, j]))
                self.tableWidget.setItem(i, j, item)
        print(display_df)

    def appendDataFrame(self, df):
        display_df = df[['customer_id', 'cluster', 'genre_diversity']]
        current_rows = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(current_rows + display_df.shape[0])
        for i in range(display_df.shape[0]):
            for j in range(display_df.shape[1]):
                item = QTableWidgetItem(str(display_df.iloc[i, j]))
                self.tableWidget.setItem(current_rows + i, j, item)
        print(display_df)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = ClusterMainWindowEx()
    ui.setupUi(MainWindow)
    MainWindow.resize(800, 600)
    MainWindow.show()
    sys.exit(app.exec())