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

## 中国主要山脉：选择练习（基于 V0.2）

原有12题迁入 `data/mountains.js`，名称、坐标、介绍与135公里容差不变。题目增加稳定 id 与基础/进阶学习分组；分组不是科学分类。`mountain-selection.js` 仅提供题目子集，打乱、判分、错题仍使用原有逻辑。

在「记忆挑战 → 地图定位 → 中国主要山脉」展开选择面板，可全选、仅选基础、仅选进阶或逐题勾选，再点击“开始所选练习”。改变勾选不立即中断当前练习；开始或重新开始时重置本轮进度。至少选一题才能开始。选择不持久化，刷新后默认全选；原有浏览器存储键及数据保持兼容。

Windows 试玩：下载本分支 ZIP，全部提取，打开 `preview` 文件夹，双击 `shanhe-mountains-preview.html`。该文件内嵌脚本样式并直接进入山脉选择面板；原地图瓦片仍需联网，没有采用 V0.3 地图或数据。查看手机布局可按 F12、Ctrl+Shift+M。

代表点只能用于本版定位练习，不表示山脉精确位置、走向或范围；原坐标仍待逐项来源核验。当前环境在线瓦片被代理拦截，真实底图显示未复测，Windows/实体手机/Safari 未实测。

重新打包只需 `python3 scripts/build_mountain_preview.py`；该脚本不改变应用和地理数据。

选择功能回归检查：先启动8000端口服务，再运行 `python3 tests/mountain_selection.py`；原有功能检查仍可运行 `python3 tests/browser_smoke.py`。独立预览仅完成 Chromium 内存载入检查，受当前环境策略限制未直接实测 file:// 双击打开。
