# 山河志 · V0.2

以地图探索为核心的中国历史自然地理互动图册。本版默认浏览陕西，提供陕北、关中、陕南三个主题；主题只移动地图视野，不绘制分区边界。

## 预览

无需构建或安装应用依赖。在仓库根目录运行：

```sh
python3 -m http.server 8000 --bind 0.0.0.0
```

通过开发环境的端口预览功能访问 8000 端口；本机开发时用浏览器访问本机 8000 端口。没有配置公开预览或部署。

Leaflet 1.9.4 随仓库提供。底图仍需联网访问 `a/b/c.tile.opentopomap.org` 和 `a/b/c.tile.openstreetmap.org`；加载失败时显示提示，可切换底图或重试。没有离线缓存或批量下载瓦片。

## 保留的功能

「记忆挑战」中保留山河定位、错题再练、历史战役、自制题库及 JSON 导入导出。继续使用原有 `shanhe_custom`、`shanhe_wrong`、`shanhe_total` 本地存储键，不迁移或清空已有数据。

## 验证

先启动上述服务。在已安装 Python Playwright 和 `/usr/bin/chromium` 的环境运行：

```sh
python3 tests/browser_smoke.py
```

测试使用独立浏览器上下文，检查三个主题视野、首页不显示挑战、答题、历史完成及重启、自制题库增删与导入导出、刷新后数据持久化、底图署名切换及 390px 手机布局。截图和导出测试文件写入 `/tmp/atlas-*`。不会修改使用者浏览器的数据。

本次 Chromium 实测交互通过，无 JavaScript 异常；当前环境的瓦片请求返回网络代理 403，因此真实地形图片、标签清晰度、成功加载后的视觉效果尚未实测。手机测试为 Chromium 触屏模拟，未测试实体手机或 Safari。

## 来源与限制

- 地形底图数据：© OpenStreetMap 贡献者（ODbL）、SRTM；制图 © OpenTopoMap（CC BY-SA 3.0）。常规底图：© OpenStreetMap 贡献者。页面和地图保留可点击署名与许可链接。
- OpenTopoMap 许可说明：https://opentopomap.org/about
- OSM 版权：https://www.openstreetmap.org/copyright
- OSM 瓦片政策：https://operations.osmfoundation.org/policies/tiles/
- CC BY-SA 3.0：https://creativecommons.org/licenses/by-sa/3.0/
- 区域文字为概括性地理导览，阅读参考指向陕西省人民政府官网；未导入新的地理空间数据。具体边界、位置与历史政区仍待逐项资料核验。官网及服务最新条款本次因网络限制未能重新读取，补充署名不代表完成所有服务政策核验。
- 栅格底图包含既有标签，暂不能独立隐藏标签。地形色彩未通过滤镜修改，以保留原有信息。
