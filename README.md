# 🎵 15-Step 音序器

一个基于 Python + PySide6 + simpleaudio 的 15 步进音序器。  
支持实时播放、可调节 BPM，适合学习合成器节奏逻辑或玩一玩音符创作！
  
## 🚀 功能特点

- 🎼 支持 7 个音符（sol la do re mi sol la），覆盖 1-6 旋律音高
- ⏱️ 15 步进序列，每步独立可编程
- 🎚️ 实时调整 BPM（60 ~ 600）
- 🔊 每个音符由自定义正弦波+锯齿波合成，带有渐强效果
- 💡 当前节拍高亮提示
- 🧼 极简深色界面风格

## 📦 安装运行

### 1. 克隆仓库

```bash
git clone https://github.com/wondersus/15-step-sequencer
cd 15-step-sequencer
```

### 2. 安装依赖

确保你使用的是 Python 3.8+，然后安装依赖：

```bash
pip install numpy simpleaudio PySide6
```

### 3. 运行程序

```bash
python sequencer.py
```

## 🎛️ 控制说明

- 🖱️ 点击方块：激活/关闭该步进的音符
- ▶ / ⏸ 按钮：播放 / 暂停
- 🎚️ 滑动条：调节 BPM（节奏速度）

## 📁 文件结构

```
15-step-sequencer/
├── sequencer.py     # 主程序
├── README.md        # 项目说明文件
```

## 💖 开发者的话

我爱你👄

## 📜 License

MIT License. Feel free to play, hack, and remix！

---

