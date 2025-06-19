import sys
import numpy as np
import simpleaudio as sa
from PySide6.QtCore import QTimer, Qt

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QSlider, QLabel, QGridLayout
)

# 音高频率（Hz），sol la do re mi sol la
NOTES_FREQ = [392, 440, 523, 587, 659, 392*2, 440*2]
NUM_STEPS = 15  # 15拍
NUM_NOTES = len(NOTES_FREQ)
SAMPLE_RATE = 48000

def generate_tone(freq, duration=0.2):
    """生成指定频率和时长的音频数据，前半为正弦波，后半为锯齿波（锯齿波音量减半），前20ms为渐强"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    half = len(t) // 2
    # 前半正弦波
    sine = np.sin(freq * t[:half] * 2 * np.pi)
    # 后半锯齿波，音量减半
    saw = 2 * (freq * t[half:] - np.floor(0.5 + freq * t[half:])) * 0.2
    # 拼接
    tone = np.concatenate([sine, saw])
    # 前20ms渐强
    fade_len = int(SAMPLE_RATE * 0.05)
    if fade_len > 0:
        fade_in = np.linspace(0, 1, fade_len)
        tone[:fade_len] *= fade_in
    audio = tone * (2**15 - 1) / np.max(np.abs(tone))
    return audio.astype(np.int16)

# 预生成所有音符的音频数据
AUDIO_CLIPS = [generate_tone(f) for f in NOTES_FREQ]

class Sequencer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("15-Step Sequencer")
        self.setStyleSheet("background-color: #1e2a38;")
        self.pattern = [[0]*NUM_STEPS for _ in range(NUM_NOTES)]  # 步进矩阵
        self.current_step = 0
        self.is_playing = False
        self.bpm = 120

        # UI布局
        layout = QGridLayout()
        layout.setSpacing(4)

        # 步进按钮
        self.step_buttons = []
        for row in range(NUM_NOTES):
            btn_row = []
            for col in range(NUM_STEPS):
                btn = QPushButton("")
                btn.setFixedSize(32, 32)
                btn.setStyleSheet(self.btn_style(0, False))
                btn.clicked.connect(self.make_toggle_handler(row, col))
                layout.addWidget(btn, row+1, col+1)
                btn_row.append(btn)
            self.step_buttons.append(btn_row)

        # 行数字标注，改为56123
        row_labels = ['5', '6', '1', '2', '3', '5', '6']
        for row in range(NUM_NOTES):
            lbl = QLabel(row_labels[row])
            lbl.setStyleSheet("color: #8ecae6; font-size: 14px;")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl, row+1, 0)

        # 列数字标注
        for col in range(NUM_STEPS):
            lbl = QLabel(str(col+1))
            lbl.setStyleSheet("color: #8ecae6; font-size: 14px;")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl, 0, col+1)

        # 播放/暂停按钮
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(66, 24)
        self.play_btn.setStyleSheet(self.ctrl_style())
        self.play_btn.clicked.connect(self.toggle_play)
        layout.addWidget(self.play_btn, NUM_NOTES+2, 1, 1, 3)

        # BPM滑块
        self.bpm_slider = QSlider(Qt.Horizontal)
        self.bpm_slider.setRange(60, 600)
        self.bpm_slider.setValue(self.bpm)
        self.bpm_slider.valueChanged.connect(self.set_bpm)
        self.bpm_slider.setStyleSheet(self.slider_style())
        layout.addWidget(self.bpm_slider, NUM_NOTES+2, 4, 1, 8)

        # BPM标签
        # self.bpm_label = QLabel(f"BPM: {self.bpm}")
        self.bpm_label = QLabel(f"{self.bpm}")
        self.bpm_label.setStyleSheet("color: #2196f3; font-size: 26px;")
        layout.addWidget(self.bpm_label, NUM_NOTES+2, 13, 1, 4)

        self.setLayout(layout)

        # 定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)

    def btn_style(self, active, highlight):
        # 极简蓝色系矩形按钮样式
        base = "#2196f3" if active else "#274472"
        border = "#8ecae6" if highlight else "#1e2a38"
        return (
            f"background-color: {base};"
            f"border: 2px solid {border};"
            "border-radius: 6px;"
        )

    def ctrl_style(self):
        # 控制按钮样式
        return (
            "background-color: #1565c0;"
            "color: white;"
            "font-size: 18px;"
            "border-radius: 8px;"
        )

    def slider_style(self):
        # 滑块样式
        return (
            "QSlider::groove:horizontal {background: #274472; height: 32px; border-radius: 12px; }"
            "QSlider::handle:horizontal {background: #2196f3; width: 18px; border-radius: 12px;}"
        )

    def make_toggle_handler(self, row, col):
        # 返回一个切换步进状态的处理函数
        def handler():
            self.pattern[row][col] ^= 1
            self.step_buttons[row][col].setStyleSheet(
                self.btn_style(self.pattern[row][col], self.current_step == col)
            )
        return handler

    def set_bpm(self, value):
        # 设置BPM
        self.bpm = value
        # self.bpm_label.setText(f"BPM: {self.bpm}")
        self.bpm_label.setText(f"{self.bpm}")
        if self.is_playing:
            self.timer.setInterval(self.step_interval())

    def step_interval(self):
        # 计算每步的间隔（毫秒）
        return int(60000 / self.bpm)

    def toggle_play(self):
        # 播放/暂停
        if self.is_playing:
            self.timer.stop()
            self.is_playing = False
            self.play_btn.setText("▶")
            self.update_highlight(-1)
        else:
            self.is_playing = True
            self.play_btn.setText("⏸")
            self.timer.start(self.step_interval())
            self.current_step = 0
            self.next_step()

    def next_step(self):
        # 播放当前步
        for row in range(NUM_NOTES):
            if self.pattern[row][self.current_step]:
                sa.play_buffer(AUDIO_CLIPS[row], 1, 2, SAMPLE_RATE)
        self.update_highlight(self.current_step)
        self.current_step = (self.current_step + 1) % NUM_STEPS

    def update_highlight(self, step):
        # 更新步进按钮高亮
        for row in range(NUM_NOTES):
            for col in range(NUM_STEPS):
                highlight = (col == step)
                self.step_buttons[row][col].setStyleSheet(
                    self.btn_style(self.pattern[row][col], highlight)
                )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Sequencer()
    w.show()
    sys.exit(app.exec())