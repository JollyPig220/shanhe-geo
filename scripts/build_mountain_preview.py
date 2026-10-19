"""Inline existing scripts/styles for double-click preview; keep the V0.2 online map."""
import base64,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'index.html').read_text()
css=(ROOT/'vendor/leaflet/leaflet.css').read_text()
for image in (ROOT/'vendor/leaflet/images').iterdir():
 css=css.replace('images/'+image.name,'data:image/png;base64,'+base64.b64encode(image.read_bytes()).decode())
html=html.replace('<link rel="stylesheet" href="vendor/leaflet/leaflet.css">','<style>'+css+'</style>')
for name in ['vendor/leaflet/leaflet.js','data/mountains.js','mountain-selection.js']:
 script=re.sub(r'//# sourceMappingURL=.*','',(ROOT/name).read_text())
 script=re.sub(r'</script',r'<\\/script',script,flags=re.I)
 html=html.replace('<script src="'+name+'"></script>','<script>'+script+'</script>')
# Preview-only entry: the website itself continues opening on the V0.2 atlas home.
html=html.replace("resetQuiz();switchTab('explore');", "resetQuiz();switchTab('quiz');document.getElementById('mountainPicker').open=true;")
html+='\n<!-- Leaflet license\n'+(ROOT/'vendor/leaflet/LICENSE').read_text()+'\n-->\n'
OUT=ROOT/'preview';OUT.mkdir(exist_ok=True)
(OUT/'shanhe-mountains-preview.html').write_text(html)
(OUT/'README.txt').write_text('''山河志 · V0.2 山脉选择练习预览\n\n下载 ZIP → 右键“全部提取” → 双击 shanhe-mountains-preview.html，用 Edge 或 Chrome 打开。\n无需安装软件或启动服务器；原有在线地图需要联网。加载失败时可切换“常规”或重试。\n预览直接进入山脉练习，勾选题目后点击“开始所选练习”。\n看手机布局：F12 → Ctrl+Shift+M → 选择手机尺寸。\n山脉仍为原有12个示范代表点，约135公里容差，不表示山脉的精确位置、走向或范围，原坐标尚待逐项来源核验。\n分组仅表示建议学习顺序，不是山脉的重要性或科学分类。\n选择只在当前页面有效，刷新后默认全选；原错题、题库、累计答题数据不迁移或清空。离线文件与线上网站的浏览器存储可能相互独立。\n当前已验证 Chromium 桌面和手机模拟交互；未实测 Windows 双击打开、实体手机或 Safari。当前环境的在线底图仍被网络策略拦截。\n''',encoding='utf-8-sig')
with zipfile.ZipFile('/tmp/shanhe-mountains-preview.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ['shanhe-mountains-preview.html','README.txt']:z.write(OUT/name,name)
print('Preview: preview/shanhe-mountains-preview.html; ZIP: /tmp/shanhe-mountains-preview.zip')
