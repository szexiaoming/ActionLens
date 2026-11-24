# ActionLens 真实结果导入说明

真实结果导入器负责将云端评测输出转换为网页可以直接读取的数据。导入前不会修改项目中的模拟记录；导入成功后，网页数据清单会切换到真实数据。

## 支持的输入形式

### 单个 JSON 文件

文件可以包含一个运行对象，也可以包含运行对象数组：

```powershell
.\.venv\Scripts\python.exe scripts\import_real_results.py incoming\runs.json
```

媒体路径相对于该 JSON 文件所在目录。

### 评测输出目录

目录根部可以包含 `runs.json`：

```text
incoming/libero-evaluation/
├── runs.json
├── videos/
└── frames/
```

也可以为每个回合保存一个 `metadata.json`：

```text
incoming/libero-evaluation/
├── task-a-normal-seed-0000/
│   ├── metadata.json
│   ├── episode.mp4
│   └── frames/
│       ├── start.png
│       ├── middle.png
│       └── end.png
└── task-a-normal-seed-0001/
    └── metadata.json
```

目录模式会递归发现所有 `metadata.json`。

## 媒体字段

`artifacts` 中的非空值必须是相对于记录文件的本地路径：

```json
{
  "videoUrl": "episode.mp4",
  "startFrameUrl": "frames/start.png",
  "middleFrameUrl": "frames/middle.png",
  "endFrameUrl": "frames/end.png"
}
```

导入器不接受绝对路径、HTTP URL 或越过导入根目录的 `../` 路径。找不到文件时导入失败，不会写入一半结果。

## 导入结果

成功导入后生成：

```text
data/real/
├── runs.json
└── summary.json

web/public/
├── data/
│   ├── manifest.json
│   ├── runs.json
│   └── summary.json
└── media/<run-id>/
    ├── video.mp4
    ├── start.png
    ├── middle.png
    └── end.png
```

原始媒体文件不会被删除或移动。

## 导入失败处理

- 修正命令输出指出的字段或文件；
- 保留原始云端输出；
- 修正后使用同一条命令重新导入；
- 不要手工修改 `web/public/data` 中的派生文件。

需要返回模拟数据时执行：

```powershell
.\.venv\Scripts\python.exe scripts\build_web_data.py --source mock
```
