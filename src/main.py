from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QFileDialog, QLabel, QVBoxLayout, QWidget, QDockWidget, QListWidget, QListWidgetItem, QProgressBar, 
    QComboBox, QFormLayout, QGroupBox, QInputDialog, QMessageBox, QColorDialog, QFontDialog, QGraphicsTextItem, QGraphicsScene, QGraphicsView
)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QTransform, QColor, QFont, QIcon
from PyQt5.QtCore import Qt, QSize, QPoint, QRect, QTimer
import sys
import os
import cv2


class SplashScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sparky Edits Loading...")
        self.setGeometry(100, 100, 500, 300)

        # Set up the splash screen layout
        self.label = QLabel("Welcome to Sparky Edits!", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.label.setGeometry(0, 50, 500, 50)

        # Progress bar for loading
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, 200, 400, 30)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                text-align: center;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #00ffcc;
            }
        """)

        # Sparky Edits logo
        self.logo_label = QLabel(self)
        pixmap = QPixmap("C:/Users/surek/OneDrive/Pictures/sparky_logo.png").scaled(100, 100)
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setGeometry(200, 100, 100, 100)





class PhotoEditor(QMainWindow):
    def __init__(self):  # Fix this method name
        super().__init__()

        self.setWindowTitle("My Photo Editor - Enhanced Edition")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize variables and UI components
        self.initialize_variables()
        self.initialize_ui()

    def initialize_variables(self):
        # Image management
        self.images = []
        self.image_names = []
        self.current_image_index = None
        self.current_image_cv = None
        self.zoom_level = 1.0
        self.rotation_angle = 0
        self.translation_offset = QPoint(0, 0)
        self.is_dragging = False
        self.drag_start = QPoint()
        # Crop mode state and crop preview variables
        self.cropping = False
        self.crop_start_point = QPoint()
        self.crop_rect = None
        self.crop_preview_item = None  # Temporary rectangle for showing crop selection
        self.crop_mode = False

        self.is_adding_text = False
        self.is_drawing_circle = False
        self.is_drawing_line = False
        self.temp_pixmap = None  # For drawing previews
        self.start_point = None  # For drawing shapes
        self.working_directory = os.path.join(os.getcwd(), "saved_images")
        os.makedirs(self.working_directory, exist_ok=True)
        self.secondary_windows = []  # To keep references to all secondary windows
        





    def initialize_ui(self):
        # Central widget and layout
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #f0f0f0;")
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.image_label)
        self.setCentralWidget(central_widget)
       

        # Set up toolbar, dock panel, and other components
        self.setup_toolbar()
        self.setup_dock_panel()
        self.setup_color_conversion()
        self.setup_image_details_panel()

    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        open_action = QAction("Open Image", self)
        open_action.triggered.connect(self.open_image_dialog)
        toolbar.addAction(open_action)

        save_action = QAction("Save Image", self)
        save_action.triggered.connect(self.save_image)
        toolbar.addAction(save_action)

        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)

        rotate_action = QAction("Rotate 90°", self)
        rotate_action.triggered.connect(self.rotate_image)
        toolbar.addAction(rotate_action)

        # Translate action
        translate_action = QAction("Translate Image", self)
        translate_action.triggered.connect(self.enable_translation)
        toolbar.addAction(translate_action)

        # Add Text action
        add_text_action = QAction("Add Text", self)
        add_text_action.triggered.connect(self.enable_text_mode)
        toolbar.addAction(add_text_action)

        blank_canvas_action = QAction("Create Blank Canvas", self)
        blank_canvas_action.triggered.connect(self.create_blank_canvas)
        toolbar.addAction(blank_canvas_action)

        change_pixel_action = QAction("Change Pixel Color", self)
        change_pixel_action.triggered.connect(self.enable_pixel_editing_mode)
        toolbar.addAction(change_pixel_action)

        draw_circle_action = QAction("Draw Circle", self)
        draw_circle_action.triggered.connect(self.enable_circle_drawing_mode)
        toolbar.addAction(draw_circle_action)

        draw_line_action = QAction("Draw Line", self)
        draw_line_action.triggered.connect(self.enable_line_drawing_mode)
        toolbar.addAction(draw_line_action)

        create_thumbnail_action = QAction("Create Thumbnail", self)
        create_thumbnail_action.triggered.connect(self.create_thumbnail)
        toolbar.addAction(create_thumbnail_action)

        combine_images_action = QAction("Combine Images", self)
        combine_images_action.triggered.connect(lambda: self.combine_images("horizontal"))
        toolbar.addAction(combine_images_action)

        combine_images_vertical_action = QAction("Combine Images Vertically", self)
        combine_images_vertical_action.triggered.connect(lambda: self.combine_images("vertical"))
        toolbar.addAction(combine_images_vertical_action)
 
        open_new_window_action = QAction("Open New Window", self)
        open_new_window_action.triggered.connect(self.open_new_window)
        toolbar.addAction(open_new_window_action)

        crop_action = QAction("Crop", self)
        crop_action.triggered.connect(self.activate_crop_mode)
        toolbar.addAction(crop_action)



    def open_new_window(self):
        """Open a new window with a copy of the current image."""
        if self.current_image_index is None:
            QMessageBox.warning(self, "No Image", "Please load an image to open in a new window.")
            return

    # Get the current image
        current_pixmap = self.images[self.current_image_index]

        new_window = SecondaryWindow(current_pixmap)
        self.secondary_windows.append(new_window)
        new_window.show()

    # Create a new window
        new_window = SecondaryWindow(current_pixmap)
        new_window.show()



    def create_thumbnail(self):
        """Create a thumbnail for the currently displayed image."""
        if self.current_image_index is None:
            QMessageBox.warning(self, "No Image", "Please load an image to create a thumbnail.")
            return

    # Get the current image
        current_pixmap = self.images[self.current_image_index]

    # Create a scaled-down version
        thumbnail_pixmap = current_pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    # Save the thumbnail
        thumbnail_path = os.path.join(self.working_directory, f"thumbnail_{self.image_names[self.current_image_index]}")
        thumbnail_pixmap.save(thumbnail_path)

        QMessageBox.information(self, "Thumbnail Created", f"Thumbnail saved at: {thumbnail_path}")


    def enable_circle_drawing_mode(self):
            """Enable circle drawing mode."""
            self.is_drawing_circle = True
            self.is_drawing_line = False
            self.image_label.setCursor(Qt.CrossCursor)
            QMessageBox.information(self, "Circle Drawing Mode", "Click and drag to draw circles.")

    def enable_line_drawing_mode(self):
        """Enable line drawing mode."""
        self.is_drawing_circle = False
        self.is_drawing_line = True
        self.image_label.setCursor(Qt.CrossCursor)
        QMessageBox.information(self, "Line Drawing Mode", "Click and drag to draw lines.")


    def create_blank_canvas(self):
        """Create a blank canvas of the specified size and color."""
        # Input dialogs for size
        width, ok_width = QInputDialog.getInt(self, "Canvas Width", "Enter the width (px):", min=1, max=5000)
        if not ok_width:
            return
        height, ok_height = QInputDialog.getInt(self, "Canvas Height", "Enter the height (px):", min=1, max=5000)
        if not ok_height:
            return
        # Color selection
        color = QColorDialog.getColor(Qt.white, self, "Select Canvas Color")
        if not color.isValid():
            color = QColor("white")  # Default to white

        # Create blank canvas
        blank_pixmap = QPixmap(width, height)
        blank_pixmap.fill(color)
        self.images.append(blank_pixmap)
        self.image_names.append(f"Blank Canvas ({width}x{height})")
        self.display_image(len(self.images) - 1)  

        self.update_image_details(f"Blank Canvas ({width}x{height})")
    
    def enable_pixel_editing_mode(self):
        """Enable pixel editing mode."""
        self.is_pixel_editing = True
        self.image_label.setCursor(Qt.CrossCursor)  # Change the cursor to indicate editing mode
        QMessageBox.information(self, "Pixel Editing Mode", "Click on the image to change pixel color.")

    def setup_dock_panel(self):
        dock = QDockWidget("Images", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.image_list_widget = QListWidget()
        self.image_list_widget.setIconSize(QSize(64, 64))
        self.image_list_widget.itemClicked.connect(self.display_selected_image)
        dock.setWidget(self.image_list_widget)

        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def setup_color_conversion(self):
        self.color_conversion_box = QComboBox()
        self.color_conversion_box.addItem("Original (RGB)")
        self.color_conversion_box.addItem("Grayscale")
        self.color_conversion_box.addItem("HSV")
        self.color_conversion_box.addItem("CIE Lab")
        self.color_conversion_box.addItem("HLS")
        self.color_conversion_box.addItem("YCrCb")
        self.color_conversion_box.currentTextChanged.connect(self.apply_color_conversion)

        self.statusBar().addPermanentWidget(QLabel("Color Space:"))
        self.statusBar().addPermanentWidget(self.color_conversion_box)

    def setup_image_details_panel(self):
        self.details_panel = QDockWidget("Image Details", self)
        self.details_panel.setAllowedAreas(Qt.RightDockWidgetArea)

        details_widget = QWidget()
        layout = QFormLayout(details_widget)
        self.details_labels = {
            "File Name": QLabel("N/A"),
            "Image Size": QLabel("N/A"),
            "Resolution": QLabel("N/A"),
            "Image Type": QLabel("N/A")
        }
        for label, widget in self.details_labels.items():
            layout.addRow(label, widget)

        self.details_panel.setWidget(details_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.details_panel)

    def update_image_details(self, file_path):
        self.details_labels["File Name"].setText(os.path.basename(file_path))
        pixmap = self.images[self.current_image_index]
        self.details_labels["Image Size"].setText(f"{pixmap.width()} x {pixmap.height()} pixels")
        self.details_labels["Resolution"].setText(f"{pixmap.width()}x{pixmap.height()} pixels")
        self.details_labels["Image Type"].setText(file_path.split(".")[-1].upper())

    def open_image_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            image = QPixmap(file_path)
            if image.isNull():
                QMessageBox.warning(self, "Error", "Failed to load image.")
                return
            self.images.append(image)
            self.image_names.append(os.path.basename(file_path))
            self.current_image_index = len(self.images) - 1  # Update the current image index
            self.add_image_thumbnail(os.path.basename(file_path))
            
           
            self.display_image(self.current_image_index)
        # Update image details
            self.update_image_details(file_path)
            self.current_image_cv = cv2.imread(file_path)
            if self.current_image_cv is not None:
                self.current_image_cv = cv2.cvtColor(self.current_image_cv, cv2.COLOR_BGR2RGB)

            self.create_thumbnail()  # Automatically create a thumbnail
            self.statusBar().showMessage(f"Image loaded: {file_path}")

    def save_image(self):
        """Save the current image or blank canvas to a file."""
        if self.current_image_index is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
            if file_path:
                self.images[self.current_image_index].save(file_path)
                self.create_thumbnail()
                QMessageBox.information(self, "Image Saved", f"Image saved successfully at {file_path}!")

    def display_image(self, index):
        """Display the selected image or blank canvas."""
        if 0 <= index < len(self.images):
            self.current_image_index = index
            pixmap = self.images[index]
            
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

    def add_image_thumbnail(self, image_name):
        """Add a thumbnail and image name to the image list."""
        if self.current_image_index is not None:
        # Get the current image and create a thumbnail
            pixmap = self.images[self.current_image_index]
            thumbnail_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Create a list item with an icon and text
            item = QListWidgetItem(QIcon(thumbnail_pixmap), image_name)
            self.image_list_widget.addItem(item)


    def display_selected_image(self, item):
        index = self.image_list_widget.row(item)
        self.display_image(index)

    def apply_color_conversion(self, color_space):
        if self.current_image_cv is None:
            return

        if color_space == "Original (RGB)":
            converted_image = self.current_image_cv
        elif color_space == "Grayscale":
            converted_image = cv2.cvtColor(self.current_image_cv, cv2.COLOR_RGB2GRAY)
        elif color_space == "HSV":
            converted_image = cv2.cvtColor(self.current_image_cv, cv2.COLOR_RGB2HSV)
        elif color_space == "CIE Lab":
            converted_image = cv2.cvtColor(self.current_image_cv, cv2.COLOR_RGB2Lab)
        elif color_space == "HLS":
            converted_image = cv2.cvtColor(self.current_image_cv, cv2.COLOR_RGB2HLS)
        elif color_space == "YCrCb":
            converted_image = cv2.cvtColor(self.current_image_cv, cv2.COLOR_RGB2YCrCb)

        self.display_converted_image(converted_image)

    def display_converted_image(self, image):
        if image.ndim == 2:  # Grayscale image
            q_image = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_Grayscale8)
        else:  # Color image
            q_image = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.images[self.current_image_index] = pixmap
        self.update_image_display()

    def zoom_in(self):
        self.zoom_level *= 1.2
        self.update_image_display()

    def zoom_out(self):
        self.zoom_level /= 1.2
        self.update_image_display()

    def rotate_image(self):
        if self.current_image_index is not None:
            self.rotation_angle += 90
            self.update_image_display()

    def update_image_display(self):
        if self.current_image_index is not None:
            pixmap = self.images[self.current_image_index]
            transformed_pixmap = pixmap.transformed(
                QTransform().rotate(self.rotation_angle)
            ).scaled(
                pixmap.size() * self.zoom_level,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # Apply translation
            display_pixmap = QPixmap(self.image_label.size())
            display_pixmap.fill(Qt.transparent)
            painter = QPainter(display_pixmap)
            painter.drawPixmap(self.translation_offset, transformed_pixmap)
            painter.end()
            self.image_label.setPixmap(display_pixmap)

    def enable_translation(self):
        self.is_dragging = True
        self.image_label.setCursor(Qt.OpenHandCursor)
    
    def perform_crop(self, rect):
            """Crop the selected area."""
            if self.current_image_index is not None:
                pixmap = self.images[self.current_image_index]
        
        # Ensure the crop rectangle is valid and within bounds
            bounded_rect = rect.intersected(pixmap.rect())
            if bounded_rect.isNull():
                QMessageBox.warning(self, "Invalid Crop", "The selected crop area is invalid.")
                return

            cropped_pixmap = pixmap.copy(bounded_rect)

        # Replace the current image with the cropped one
            self.images[self.current_image_index] = cropped_pixmap
            self.display_image(self.current_image_index)
            self.statusBar().showMessage("Image cropped successfully.")


    def mousePressEvent(self, event):
        if self.crop_mode and event.button() == Qt.LeftButton:
            if self.current_image_index is not None:
            # Map mouse position to image coordinates
                label_size = self.image_label.size()
                pixmap_size = self.images[self.current_image_index].size()
                scale_x = pixmap_size.width() / label_size.width()
                scale_y = pixmap_size.height() / label_size.height()
            
            # Map the start point to image coordinates
                self.crop_start_point = QPoint(
                    int(event.pos().x() * scale_x),
                    int(event.pos().y() * scale_y)
                )

        print(f"Crop started at: {self.crop_start_point}")  # Debug print
            
            # Initialize cropping state and rectangle
        self.cropping = True
        self.crop_rect = QRect(self.crop_start_point, self.crop_start_point)

            
        if self.is_drawing_circle or self.is_drawing_line:
                    self.start_point = event.pos()
                    self.temp_pixmap = self.image_label.pixmap().copy()  # Create a temporary pixmap
         # Handle adding text
        if self.is_adding_text and event.button() == Qt.LeftButton:
            self.add_text(event.pos())
        return
            
    def mouseMoveEvent(self, event):
        if hasattr(self, 'is_pixel_editing') and self.is_pixel_editing and event.buttons() & Qt.LeftButton:
            if self.current_image_index is not None:
                label_size = self.image_label.size()
                pixmap = self.image_label.pixmap()
            if pixmap is None:
                return

            image_size = pixmap.size()
            scale_x = image_size.width() / label_size.width()
            scale_y = image_size.height() / label_size.height()

            image_x = int(event.x() * scale_x)
            image_y = int(event.y() * scale_y)

            if 0 <= image_x < image_size.width() and 0 <= image_y < image_size.height():
                self.change_pixel_color(image_x, image_y)

        if self.is_dragging and event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.drag_start
            self.translation_offset += delta
            self.drag_start = event.pos()
            self.update_image_display()
        if self.cropping and self.crop_start_point:
            if self.current_image_index is not None:
            # Map mouse position to image coordinates
                label_size = self.image_label.size()
                pixmap_size = self.images[self.current_image_index].size()
                scale_x = pixmap_size.width() / label_size.width()
                scale_y = pixmap_size.height() / label_size.height()

            # Calculate the current point in image coordinates
                current_point = QPoint(
                    int(event.pos().x() * scale_x),
                    int(event.pos().y() * scale_y)
                )

                print(f"Crop updated to: Start={self.crop_start_point}, End={current_point}")  # Debug print


            # Update the cropping rectangle
                self.crop_rect = QRect(self.crop_start_point, current_point).normalized()

            # Create a preview of the cropping rectangle
                temp_pixmap = self.images[self.current_image_index].copy()
                painter = QPainter(temp_pixmap)
                pen = QPen(Qt.yellow, 2, Qt.DashLine)
                painter.setPen(pen)
                painter.drawRect(self.crop_rect)
                painter.end()

            # Update the QLabel with the preview pixmap
                self.image_label.setPixmap(temp_pixmap)

        if (self.is_drawing_circle or self.is_drawing_line) and self.start_point:
                preview_pixmap = self.temp_pixmap.copy()  # Create a copy for preview
                painter = QPainter(preview_pixmap)
                pen = QPen(Qt.red, 2, Qt.SolidLine)  # Customize pen for preview
                painter.setPen(pen)

                if self.is_drawing_circle:
                     # Calculate radius and draw circle
                    radius = int(((event.x() - self.start_point.x()) ** 2 + (event.y() - self.start_point.y()) ** 2) ** 0.5)
                    painter.drawEllipse(self.start_point, radius, radius)
                elif self.is_drawing_line:
            # Draw a line from start_point to current position
                    painter.drawLine(self.start_point, event.pos())

                painter.end()
                self.image_label.setPixmap(preview_pixmap)  # Update label with preview pixmap

               
        
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_drawing_circle or self.is_drawing_line:
                if self.image_label.pixmap() is not None and self.start_point is not None:
                # Ensure we have a valid pixmap and a start point
                    final_pixmap = self.image_label.pixmap().copy()
                    painter = QPainter(final_pixmap)
                    pen = QPen(Qt.black, 2, Qt.SolidLine)  # Final pen for drawing
                    painter.setPen(pen)

                    if self.is_drawing_circle:
                    # Draw finalized circle
                        radius = int(((event.x() - self.start_point.x()) ** 2 + (event.y() - self.start_point.y()) ** 2) ** 0.5)
                        painter.drawEllipse(self.start_point, radius, radius)
                    elif self.is_drawing_line:
                    # Draw finalized line
                        painter.drawLine(self.start_point, event.pos())

                    painter.end()  # End the painter after finishing the drawing
                    self.images[self.current_image_index] = final_pixmap  # Save the modified pixmap
                    self.display_image(self.current_image_index)  # Refresh display
                else:
                    QMessageBox.warning(self, "Drawing Error", "Unable to draw on the image.")
        
        # Reset the drawing state
            self.start_point = None

    # Handle other modes like dragging or cropping
        if self.is_dragging and event.button() == Qt.LeftButton:
            self.image_label.setCursor(Qt.OpenHandCursor)
        if event.button() == Qt.LeftButton:
            if self.crop_mode and event.button() == Qt.LeftButton:
                if self.cropping and self.crop_rect:
                    print(f"Final crop rectangle: {self.crop_rect}")  # Debug print
            # Finalize the crop
                    cropped_pixmap = self.images[self.current_image_index].copy(self.crop_rect)
                self.images[self.current_image_index] = cropped_pixmap
                self.display_image(self.current_image_index)
            
            # Reset cropping state
                self.cropping = False
                self.crop_mode = False
                self.statusBar().showMessage("Image cropped successfully.")


    def activate_crop_mode(self):
        """Activate crop mode."""
        self.crop_mode = True
        self.statusBar().showMessage("Crop mode activated. Drag to select area.")

    def deactivate_crop_mode(self):
        """Deactivate crop mode."""
        self.crop_mode = False
        self.statusBar().clearMessage()
        self.image_label.setCursor(Qt.ArrowCursor)

    



    # Text Adding Feature
    def enable_text_mode(self):
        """Enable text adding mode."""
        self.is_text_movable = True
        self.statusBar().showMessage("Text mode activated. Click on the image to add text.")
        self.image_label.setCursor(Qt.CrossCursor)  # Set cursor to cross for text mode

    # Text Adding Feature
    def enable_text_mode(self):
        self.is_adding_text = True
        self.image_label.setCursor(Qt.IBeamCursor)

    def add_text(self, position):
        if self.current_image_index is not None:
            text, ok = QInputDialog.getText(self, "Add Text", "Enter text:")
            if ok and text:
                # Choose font
                font, ok_font = QFontDialog.getFont()
                if not ok_font:
                    font = QFont("Arial", 20)

                # Choose color
                color = QColorDialog.getColor()
                if not color.isValid():
                    color = QColor("black")

                # Map the click position to the image coordinate system
                pixmap = self.images[self.current_image_index]
                scale_x = pixmap.width() / self.image_label.width()
                scale_y = pixmap.height() / self.image_label.height()
                image_x = int(position.x() * scale_x)
                image_y = int(position.y() * scale_y)

                # Draw text onto the image
                painter = QPainter(pixmap)
                painter.setFont(font)
                painter.setPen(QPen(color))
                painter.drawText(image_x, image_y, text)
                painter.end()

                self.update_image_display()
                self.is_adding_text = False
                self.image_label.setCursor(Qt.ArrowCursor)


    def change_pixel_color(self, x, y):
        """Change the color of a specific pixel."""
        new_color = QColorDialog.getColor(Qt.white, self, "Select Pixel Color")
        if not new_color.isValid():
            return  # User canceled the color selection

    # Access the current image
        image = self.images[self.current_image_index].toImage()
        image.setPixel(x, y, new_color.rgb())

    # Update the pixmap with the modified image
        updated_pixmap = QPixmap.fromImage(image)
        self.images[self.current_image_index] = updated_pixmap
        self.display_image(self.current_image_index)

        QMessageBox.information(self, "Pixel Color Changed", f"Pixel at ({x}, {y}) has been updated.")

    def enable_pixel_editing_mode(self):
        """Enable pixel editing mode and let the user choose a color."""
        self.is_pixel_editing = True
        self.image_label.setCursor(Qt.CrossCursor)  # Set cursor for editing mode

    # Open color picker dialog
        selected_color = QColorDialog.getColor(Qt.white, self, "Select Pixel Color")
        if not selected_color.isValid():
            QMessageBox.warning(self, "No Color Selected", "You didn't select a color. Pixel editing mode canceled.")
            self.is_pixel_editing = False
            self.image_label.setCursor(Qt.ArrowCursor)  # Reset cursor
            return

    # Store the selected color for pixel editing
        self.selected_color = selected_color
        QMessageBox.information(self, "Pixel Editing Mode", "Click on the image to change pixel colors.")


    def combine_images(self, direction="horizontal"):
        """Combine multiple images either horizontally or vertically."""
        if len(self.images) < 2:
            QMessageBox.warning(self, "Insufficient Images", "Load at least two images to combine.")
            return

        # Convert all QPixmap images to QImage for manipulation
        qimages = [pixmap.toImage() for pixmap in self.images]

    # Determine dimensions of the combined image
        if direction == "horizontal":
            total_width = sum(image.width() for image in qimages)
            max_height = max(image.height() for image in qimages)
            combined_image = QImage(total_width, max_height, QImage.Format_ARGB32)
        elif direction == "vertical":
            max_width = max(image.width() for image in qimages)
            total_height = sum(image.height() for image in qimages)
            combined_image = QImage(max_width, total_height, QImage.Format_ARGB32)
        else:
            QMessageBox.warning(self, "Invalid Direction", "Direction must be 'horizontal' or 'vertical'.")
            return

        combined_image.fill(Qt.transparent)
        painter = QPainter(combined_image)

    # Draw each image in sequence
        offset_x, offset_y = 0, 0
        for image in qimages:
            if direction == "horizontal":
                painter.drawImage(offset_x, 0, image)
                offset_x += image.width()
            else:  # vertical
                painter.drawImage(0, offset_y, image)
                offset_y += image.height()

        painter.end()

        # Convert combined QImage back to QPixmap and add to the image list
        combined_pixmap = QPixmap.fromImage(combined_image)
        self.images.append(combined_pixmap)
        self.image_names.append(f"Combined Image ({direction.capitalize()})")
        self.display_image(len(self.images) - 1)

        QMessageBox.information(self, "Combine Images", "Images combined successfully!")


    def closeEvent(self, event):
        # Reset modes when closing
        self.is_adding_text = False
        self.is_cropping = False
        self.is_dragging = False
        self.is_pixel_editing = False
        self.is_drawing_circle = False
        self.is_drawing_line = False
        self.start_point = None  # Starting point for drawing primitives
        self.temp_pixmap = None  # Temporary pixmap for drawing previews
        self.image_label.setCursor(Qt.ArrowCursor)
        event.accept()




class SecondaryWindow(QMainWindow):
        def __init__(self, pixmap):
            super().__init__()
            self.setWindowTitle("Image Manipulation Window")
            self.setGeometry(200, 200, 800, 600)
            self.pixmap = pixmap

            # Display the image
            self.image_label = QLabel(self)
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setPixmap(self.pixmap)
            self.setCentralWidget(self.image_label)

        # Manipulation Attributes
            self.pixmap = pixmap
            self.zoom_level = 1.0
            self.rotation_angle = 0

        # Toolbar for manipulations
            self.setup_toolbar()


           

        def setup_toolbar(self):
            toolbar = QToolBar("Image Manipulation Toolbar", self)
            self.addToolBar(toolbar)

        # Zoom In
            zoom_in_action = QAction("Zoom In", self)
            zoom_in_action.triggered.connect(self.zoom_in)
            toolbar.addAction(zoom_in_action)

        # Zoom Out
            zoom_out_action = QAction("Zoom Out", self)
            zoom_out_action.triggered.connect(self.zoom_out)
            toolbar.addAction(zoom_out_action)

        # Rotate
            rotate_action = QAction("Rotate", self)
            rotate_action.triggered.connect(self.rotate_image)
            toolbar.addAction(rotate_action)


        def zoom_in(self):
            self.zoom_level *= 1.2
            self.update_image_display()

        def zoom_out(self):
            self.zoom_level /= 1.2
            self.update_image_display()

        def rotate_image(self):
            self.rotation_angle += 90
            self.update_image_display()

        def update_image_display(self):
            transformed_pixmap = self.pixmap.transformed(
                QTransform().rotate(self.rotation_angle)
            ).scaled(
                self.pixmap.size() * self.zoom_level,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(transformed_pixmap)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set up and display splash screen
    splash = SplashScreen()
    splash.show()

    # Simulate loading process
    for i in range(101):
        QTimer.singleShot(i * 30, lambda value=i: splash.progress_bar.setValue(value))

    def start_editor():
        splash.close()
        editor = PhotoEditor()
        editor.show()

    # Start main window after splash
    QTimer.singleShot(3000, start_editor)

    sys.exit(app.exec_())


