import cv2
import numpy as np
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QPolygon

from .gui_signal import gui_signal


class VideoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mouse_pos = None
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setText("Right-click to interact")
        self.real_resolution = (0, 0) 
        self.zoom_offset = (0, 0)

        # for zoom & square algo
        self.selection_start = None
        self.selection_end = None
        self.is_dragging = False

        # for polygon algo
        self.polygon_points = []

    def mousePressEvent(self, event):
        pixmap = self.pixmap()
        if not pixmap or pixmap.isNull():
            super().mousePressEvent(event)
            return

        pix_size = pixmap.size()
        lbl_size = self.size()
        x_off = (lbl_size.width() - pix_size.width()) // 2
        y_off = (lbl_size.height() - pix_size.height()) // 2
        image_rect = QRect(x_off, y_off, pix_size.width(), pix_size.height())

        mode = getattr(self.parent(), 'current_tool', 'zoom')

        if event.button() == Qt.LeftButton:
            if image_rect.contains(event.pos()):
                if mode == "polygon":
                    self.handle_polygon_click(event.pos())
                    return
                else:
                    self.selection_start = event.pos()
                    self.selection_end = event.pos()
                    self.is_dragging = True

        elif event.button() == Qt.RightButton:
            if mode == "polygon" and self.polygon_points:
                if len(self.polygon_points) >= 3:
                    self.finish_polygon()
                else:
                    self.cancel_polygon()
                event.accept()
                return

        super().mousePressEvent(event)

    def handle_polygon_click(self, pos):
        if not self.polygon_points:
            self.polygon_points.append(pos)
        else:
            # Check if clicked near the start point to close the polygon
            start_pt = self.polygon_points[0]
            dist = np.hypot(pos.x() - start_pt.x(), pos.y() - start_pt.y())
            if dist < 12 and len(self.polygon_points) >= 3:
                self.finish_polygon()
                return
            self.polygon_points.append(pos)
        self.update()

    def mouseDoubleClickEvent(self, event):
        mode = getattr(self.parent(), 'current_tool', 'zoom')
        if mode == "polygon":
            if len(self.polygon_points) >= 3:
                self.finish_polygon()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_S or event.text().lower() == 's') and (event.modifiers() & Qt.ControlModifier):
            parent = self.parent()
            if parent and hasattr(parent, 'main_window') and hasattr(parent.main_window, 'capture_image'):
                parent.main_window.capture_image()
            event.accept()
            return

        mode = getattr(self.parent(), 'current_tool', 'zoom')
        if mode == "polygon" and self.polygon_points:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if len(self.polygon_points) >= 3:
                    self.finish_polygon()
                return
            elif event.key() == Qt.Key_Escape:
                self.cancel_polygon()
                return
        elif event.key() == Qt.Key_Escape:
            parent = self.parent()
            if hasattr(parent, 'is_enlarged') and parent.is_enlarged:
                parent.toggle_enlarge()
                event.accept()
                return
            elif hasattr(parent, 'is_fullscreen_window') and parent.is_fullscreen_window:
                parent.exit_fullscreen_window()
                event.accept()
                return
        super().keyPressEvent(event)

    def finish_polygon(self):
        if len(self.polygon_points) >= 3:
            real_pts = [self.map_to_real(pt) for pt in self.polygon_points]
            pts_arr = np.array(real_pts, dtype=np.float32)
            area = float(cv2.contourArea(pts_arr))
            
            if area >= 2:
                measurement = {
                    'type': 'polygon',
                    'real_points': real_pts,
                    'area': area
                }
                parent = self.parent()
                if hasattr(parent, 'measurements'):
                    parent.measurements.append(measurement)
        self.polygon_points = []
        self.update()

    def cancel_polygon(self):
        self.polygon_points = []
        self.update()

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()
        pixmap = self.pixmap()
        if self.is_dragging and pixmap and not pixmap.isNull():
            pix_size = pixmap.size()
            lbl_size = self.size()
            x_off = (lbl_size.width() - pix_size.width()) // 2
            y_off = (lbl_size.height() - pix_size.height()) // 2
            
            # Constrain the end point to the image boundaries
            mx = max(x_off, min(event.pos().x(), x_off + pix_size.width()))
            my = max(y_off, min(event.pos().y(), y_off + pix_size.height()))
            
            self.selection_end = QPoint(mx, my)
            
        parent = self.parent()
        if parent and hasattr(parent, 'coord_val_label'):
            tx, ty = self.map_to_real(event.pos())
            parent.coord_val_label.setText(f"Pos: [{tx}, {ty}]")

        self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            if self.selection_start and self.selection_end and self.parent():
                if hasattr(self.parent(), 'handle_selection'):
                    self.parent().handle_selection(self.selection_start, self.selection_end)
            self.selection_start = None
            self.selection_end = None
            self.update()
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        self.mouse_pos = None
        parent = self.parent()
        if parent and hasattr(parent, 'coord_val_label'):
            parent.coord_val_label.setText("Pos: [0, 0]")
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        pixmap = self.pixmap()
        if not pixmap or pixmap.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pix_size = pixmap.size()
        lbl_size = self.size()
        x_off = (lbl_size.width() - pix_size.width()) // 2
        y_off = (lbl_size.height() - pix_size.height()) // 2
        image_rect = QRect(x_off, y_off, pix_size.width(), pix_size.height())

        if self.mouse_pos and image_rect.contains(self.mouse_pos):
            guide_pen = QPen(QColor(255, 255, 255, 100), 1)
            guide_pen.setStyle(Qt.DashLine)
            painter.setPen(guide_pen)
            
            mx, my = self.mouse_pos.x(), self.mouse_pos.y()
            painter.drawLine(mx, image_rect.top(), mx, image_rect.bottom())
            painter.drawLine(image_rect.left(), my, image_rect.right(), my)
            tx, ty = self.map_to_real(self.mouse_pos)
            self.last_true_pos = (tx, ty)
        else:
            self.last_true_pos = (0, 0)

        painter.setClipRect(image_rect)

        # Draw completed measurements
        measurements = getattr(self.parent(), 'measurements', [])
        for m in measurements:
            m_type = m.get('type')
            if m_type == "length":
                p1 = self.real_to_screen(m['real_p1'])
                p2 = self.real_to_screen(m['real_p2'])
                color = QColor(255, 0, 255, 180)
                painter.setPen(QPen(color, 2))
                painter.drawLine(p1, p2)
                if image_rect.contains(p2):
                    self._draw_label(painter, p2, f"{m['length']:.2f} px", color)

            elif m_type in ("square", "area"):
                p1 = self.real_to_screen(m['real_p1'])
                p2 = self.real_to_screen(m['real_p2'])
                color = QColor(255, 255, 0, 180)
                painter.setPen(QPen(color, 1))
                painter.setBrush(QColor(255, 255, 0, 30))
                painter.drawRect(QRect(p1, p2).normalized())
                if image_rect.contains(p1):
                    self._draw_label(painter, p1, f"{m['area']:.2f} px²", color)

            elif m_type == "polygon":
                real_pts = m.get('real_points', [])
                if len(real_pts) >= 3:
                    screen_pts = [self.real_to_screen(rp) for rp in real_pts]
                    color = QColor(0, 230, 255, 200) # Bright cyan for polygon
                    painter.setPen(QPen(color, 2))
                    painter.setBrush(QColor(0, 230, 255, 40))
                    
                    poly = QPolygon(screen_pts)
                    painter.drawPolygon(poly)
                    
                    # Draw vertex points
                    painter.setBrush(color)
                    for pt in screen_pts:
                        painter.drawEllipse(pt, 3, 3)
                    
                    # Centroid for label
                    cx = sum(p.x() for p in screen_pts) // len(screen_pts)
                    cy = sum(p.y() for p in screen_pts) // len(screen_pts)
                    label_pos = QPoint(cx, cy)
                    if image_rect.contains(label_pos):
                        self._draw_label(painter, label_pos, f"{m['area']:.2f} px²", color)

        # Draw in-progress polygon
        mode = getattr(self.parent(), 'current_tool', 'zoom')
        if mode == "polygon" and self.polygon_points:
            color = QColor(0, 230, 255)
            painter.setPen(QPen(color, 2))
            painter.setBrush(color)
            
            # Draw existing vertices and edges
            for i in range(len(self.polygon_points)):
                pt = self.polygon_points[i]
                painter.drawEllipse(pt, 3, 3)
                if i > 0:
                    painter.drawLine(self.polygon_points[i - 1], pt)
            
            # Dynamic line to mouse cursor
            if self.mouse_pos and image_rect.contains(self.mouse_pos):
                dash_pen = QPen(color, 2, Qt.DashLine)
                painter.setPen(dash_pen)
                painter.drawLine(self.polygon_points[-1], self.mouse_pos)
                
                # Faint line back to start point
                if len(self.polygon_points) >= 2:
                    start_pt = self.polygon_points[0]
                    dist_to_start = np.hypot(self.mouse_pos.x() - start_pt.x(), self.mouse_pos.y() - start_pt.y())
                    
                    if dist_to_start < 12 and len(self.polygon_points) >= 3:
                        # Highlight start point to indicate closing
                        painter.setPen(QPen(QColor(255, 50, 50), 2))
                        painter.setBrush(Qt.NoBrush)
                        painter.drawEllipse(start_pt, 7, 7)
                    else:
                        faint_pen = QPen(QColor(0, 230, 255, 100), 1, Qt.DotLine)
                        painter.setPen(faint_pen)
                        painter.drawLine(self.mouse_pos, start_pt)

        # Draw in-progress drag (length / square / zoom)
        elif self.is_dragging and self.selection_start and self.selection_end:
            color = QColor(255, 0, 255) if mode == "length" else QColor(255, 255, 0)
            painter.setPen(QPen(color, 2, Qt.DashLine))
            
            if mode == "length":
                painter.drawLine(self.selection_start, self.selection_end)
            elif mode in ("area", "square", "zoom"):
                painter.setBrush(QColor(color.red(), color.green(), 0, 40))
                painter.drawRect(QRect(self.selection_start, self.selection_end).normalized())

        painter.end()

    def _draw_label(self, painter, pos, text, color):
        """Helper to draw text with a small dark background for visibility"""
        painter.save()
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        
        metrics = painter.fontMetrics()
        rect = metrics.boundingRect(text)
        rect.moveTopLeft(QPoint(pos.x() + 5, pos.y() - 15))
        rect.adjust(-2, -2, 2, 2)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 150))
        painter.drawRoundedRect(rect, 2, 2)
        
        painter.setPen(Qt.white)
        painter.drawText(pos.x() + 5, pos.y() - 5, text)
        painter.restore()

    def map_to_real(self, pos):
        """Maps mouse click position on UI label directly to real image pixel coordinates."""
        pixmap = self.pixmap()
        if not pixmap or pixmap.isNull():
            return 0, 0

        pix_size = pixmap.size()
        lbl_size = self.size()
        
        # Calculate offset caused by Qt.KeepAspectRatio centering
        x_off = (lbl_size.width() - pix_size.width()) // 2
        y_off = (lbl_size.height() - pix_size.height()) // 2
        
        rel_x = pos.x() - x_off
        rel_y = pos.y() - y_off
        
        # Determine the visible source field (full or zoom crop)
        parent = self.parent()
        zoom_rect = getattr(parent, 'zoom_rect', None)
        if zoom_rect:
            _, _, active_w, active_h = zoom_rect
        else:
            active_w, active_h = self.real_resolution
            if active_w <= 0 or active_h <= 0:
                active_w, active_h = pix_size.width(), pix_size.height()

        # Calculate scale factor between UI pixmap and real resolution
        scale_x = active_w / float(pix_size.width()) if pix_size.width() > 0 else 1.0
        scale_y = active_h / float(pix_size.height()) if pix_size.height() > 0 else 1.0
        
        # Map back to absolute coordinates
        real_x = int(rel_x * scale_x) + self.zoom_offset[0]
        real_y = int(rel_y * scale_y) + self.zoom_offset[1]

        # Clamp to bounds if known
        if self.real_resolution[0] > 0 and self.real_resolution[1] > 0:
            real_x = max(0, min(real_x, self.real_resolution[0] - 1))
            real_y = max(0, min(real_y, self.real_resolution[1] - 1))
        
        return real_x, real_y
    
    def real_to_screen(self, real_pt):
        pixmap = self.pixmap()
        if not pixmap or pixmap.isNull():
            return QPoint(0, 0)
        
        rx, ry = real_pt
        ox, oy = self.zoom_offset
        
        parent = self.parent()
        zoom_rect = getattr(parent, 'zoom_rect', None)
        if zoom_rect:
            _, _, lw, lh = zoom_rect
        else:
            lw, lh = self.real_resolution
            if lw <= 0 or lh <= 0:
                lw, lh = pix_size.width(), pix_size.height()
            
        pix_size = pixmap.size()
        lbl_size = self.size()
        
        scale_x = pix_size.width() / lw if lw > 0 else 1
        scale_y = pix_size.height() / lh if lh > 0 else 1
        
        x_off = (lbl_size.width() - pix_size.width()) // 2
        y_off = (lbl_size.height() - pix_size.height()) // 2
        
        sx = int((rx - ox) * scale_x) + x_off
        sy = int((ry - oy) * scale_y) + y_off

        self.last_image_rect = QRect(x_off, y_off, pix_size.width(), pix_size.height())
        
        return QPoint(sx, sy)
