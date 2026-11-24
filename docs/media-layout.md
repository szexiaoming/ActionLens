# ActionLens 媒体文件约定

每个回合最多包含一个完整视频和三张关键帧。缺少某项素材时，对应 JSON 字段使用 `null`，页面显示缺失状态。

## 云端输出命名

推荐每个回合使用独立目录：

```text
<run-id>/
├── metadata.json
├── episode.mp4
└── frames/
    ├── start.png
    ├── middle.png
    └── end.png
```

允许使用其他文件名，但 `metadata.json` 必须填写正确的相对路径。

## 网页媒体命名

导入器会统一重命名并复制到：

```text
web/public/media/<run-id>/
├── video.<原扩展名>
├── start.<原扩展名>
├── middle.<原扩展名>
└── end.<原扩展名>
```

网页 JSON 中保存 `/media/<run-id>/<文件名>`，不保存 Windows 或 Linux 的绝对路径。

## 格式建议

- 视频优先使用浏览器支持良好的 MP4；
- 关键帧使用 PNG 或 JPEG；
- 视频保留完整回合，不只保留成功片段；
- 关键帧分别对应动作开始、中间阶段和最后有效画面；
- 失败案例可以在人工复核说明中记录额外时间点，不需要复制第二份视频。
