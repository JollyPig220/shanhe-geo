"""Package the unchanged V0.3 atlas as a file://-compatible preview.
No GIS transformation, minification or third-party downloads occur here.
"""
import base64,hashlib,json,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'preview'
OUT.mkdir(exist_ok=True)
def data_url(path,mime):
 return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode('ascii')
def safe_script(text):return re.sub(r'</script',r'<\\/script',text,flags=re.I)
html=(ROOT/'index.html').read_text()
css=(ROOT/'vendor/leaflet/leaflet.css').read_text()
for image in (ROOT/'vendor/leaflet/images').iterdir():
 css=css.replace('images/'+image.name,data_url(image,'image/png'))
html=html.replace('<link rel="stylesheet" href="vendor/leaflet/leaflet.css">','<style>'+css+'</style>')
html=html.replace('<link rel="stylesheet" href="national-atlas.css">','<style>'+(ROOT/'national-atlas.css').read_text()+'</style>')
leaflet=(ROOT/'vendor/leaflet/leaflet.js').read_text()
leaflet=re.sub(r'//# sourceMappingURL=.*','',leaflet)
html=html.replace('<script src="vendor/leaflet/leaflet.js"></script>','<script>'+safe_script(leaflet)+'</script>')
# Preserve the exact existing JSON bytes and image bytes, changing only their delivery.
geo=(ROOT/'data/provinces-preview.geojson').read_bytes()
geo64=base64.b64encode(geo).decode('ascii')
js=(ROOT/'national-atlas.js').read_text()
js=js.replace("'data/china-relief.jpg'",json.dumps(data_url(ROOT/'data/china-relief.jpg','image/jpeg')))
old="""const response=await fetch('data/provinces-preview.geojson');
        if(!response.ok) throw new Error('HTTP '+response.status);
        const data=await response.json();"""
new="const data=JSON.parse(new TextDecoder().decode(Uint8Array.from(atob('"+geo64+"'), c=>c.charCodeAt(0))));"
assert js.count(old)==1
js=js.replace(old,new)
html=html.replace('<script src="national-atlas.js"></script>','<script>'+safe_script(js)+'</script>')
# Keep references readable even if the single HTML is moved away from the ZIP.
for file,mime in [('data/sources.json','application/json'),('data/README.md','text/plain;charset=utf-8'),('data/NATURAL_EARTH_LICENSE.md','text/plain;charset=utf-8')]:
 # Embedded reference documents open in the same offline file via a details block.
 label={'data/sources.json':'来源清单','data/README.md':'核验说明','data/NATURAL_EARTH_LICENSE.md':'原许可'}[file]
 import html as html_module
 html=html.replace('<a href="'+file+'">'+label+'</a>', '<a href="#offlineReferences">'+label+'</a>')
refs=''.join('<details><summary>'+label+'</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere">'+html_module.escape((ROOT/file).read_text())+'</pre></details>' for file,label in [('data/sources.json','来源清单'),('data/README.md','核验说明'),('data/NATURAL_EARTH_LICENSE.md','Natural Earth 原许可'),('vendor/leaflet/LICENSE','Leaflet 原许可')])
html=html.replace('</aside>','<details class="sources" id="offlineReferences"><summary>离线资料与许可全文</summary>'+refs+'</details></aside>')
assert '<script src=' not in html and '<link rel="stylesheet"' not in html
assert "fetch('data/provinces-preview.geojson')" not in html
preview=OUT/'shanhe-v0.3-preview.html';preview.write_text(html)
(OUT/'README.txt').write_text('''山河志 V0.3 · 离线资料预览\n\n1. 将 ZIP 下载到 Windows 电脑，右键 → 全部提取。\n2. 双击 shanhe-v0.3-preview.html，用 Edge 或 Chrome 打开。\n3. 不用安装 Python，不用运行命令，不用启动服务器；全国总图无需联网。\n4. 可操作省界和名称开关、点击高亮、选择省区、聚焦、拖动与缩放。\n5. 看手机布局：按 F12，再按 Ctrl+Shift+M，选择手机尺寸或输入宽度 390；再次按快捷键退出。部分电脑需按 Fn+F12。\n\n地形与 GeoJSON 原文件字节未修改，只内嵌到 HTML。此包仅供体验，现代政区和领土/岛礁表达尚未完成权威核验，不作为正式行政地图发布。\n陕西和记忆挑战入口保留；原有在线底图仍需联网。file:// 下的本地存储与线上网站相互独立，不会迁移或删除线上已有数据。\n当前环境禁止 file:// 导航；已通过 Linux Chromium 独立 HTML 内存载入的桌面/手机模拟检查。未直接验证 Windows 双击打开、Windows Edge、Safari 或实体手机。\n''',encoding='utf-8-sig')
manifest={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['data/provinces-preview.geojson','data/china-relief.jpg']}
(OUT/'original-data-sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
zip_path=Path('/tmp/shanhe-v0.3-windows-preview.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for path in sorted(OUT.iterdir()):z.write(path,path.name)
print(preview);print(zip_path);print('Single HTML bytes:',preview.stat().st_size)
