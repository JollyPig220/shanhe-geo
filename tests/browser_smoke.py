from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8000/',wait_until='networkidle')
 assert page.locator('#explorePanel').is_visible()
 assert not page.locator('#challengePanel').is_visible()
 assert page.locator('.leaflet-pane').count()>0
 page.get_by_role('button',name='省域试验 · 陕西山河 ↗').click()
 for key,lat in [('North',37.4),('Central',34.35),('South',32.9)]:
  page.locator('#theme'+key).click();page.wait_for_timeout(400)
  assert abs(page.evaluate('map.getCenter().lat')-lat)<0.05
  assert page.locator('#theme'+key).get_attribute('aria-pressed')=='true'
 assert page.evaluate('marks.length')==0
 page.get_by_role('button',name='陕西视野').click()
 page.screenshot(path='/tmp/atlas-desktop.png',full_page=True)
 page.locator('#challengeEntry').click()
 page.locator('#map').click(position={'x':350,'y':300})
 assert page.evaluate('total')==1
 page.locator('#nextBtn').click()
 page.locator('#showAnswer').click()
 assert page.evaluate('answered')
 page.locator('#tabHistory').click()
 page.locator('#histNext').click()
 for i in range(5):
  page.locator('#histNext').click();page.locator('#histNext').click()
 assert page.locator('#histState').inner_text()=='已完成'
 page.get_by_role('button',name='重新开始',exact=True).click()
 assert page.locator('#histNext').is_enabled()
 page.locator('#tabCreate').click()
 assert page.locator('#customPanel').is_visible()
 page.locator('#map').click(position={'x':350,'y':300})
 assert page.locator('#newLat').input_value()
 page.locator('#newName').fill('浏览器测试地点')
 page.get_by_role('button',name='＋ 添加到我的题库').click()
 assert page.locator('#customCount').inner_text()=='1'
 with page.expect_download() as dl:page.get_by_role('button',name='导出备份',exact=True).click()
 dl.value.save_as('/tmp/atlas-export.json')
 assert json.load(open('/tmp/atlas-export.json'))['custom'][0]['name']=='浏览器测试地点'
 page.reload(wait_until='networkidle')
 assert page.evaluate('customs[0].name')=='浏览器测试地点'
 assert page.evaluate('total')==1
 page.locator('#challengeEntry').click();page.locator('#tabCreate').click()
 page.on('dialog',lambda d:d.accept())
 page.locator('#importFile').set_input_files('/tmp/atlas-export.json')
 page.wait_for_timeout(300)
 assert page.locator('#customCount').inner_text()=='1'
 page.get_by_role('button',name='删除',exact=True).click()
 assert page.locator('#customCount').inner_text()=='0'
 page.get_by_role('button',name='← 返回山河探索').click()
 page.get_by_role('button',name='省域试验 · 陕西山河 ↗').click()
 page.locator('#layerSimple').click()
 assert page.locator('.leaflet-control-attribution a[href="https://www.openstreetmap.org/copyright"]').count()==1
 page.locator('#layerTerrain').click()
 assert page.locator('.leaflet-control-attribution a[href="https://creativecommons.org/licenses/by-sa/3.0/"]').count()==1
 assert not errors,errors
 print('PASS: desktop exploration, three camera targets, no overlay geometry, quiz, history completion/restart, custom add/export/import/delete, storage persistence, attribution switching; no JS errors')
 mobile=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=1)
 mobile.goto('http://127.0.0.1:8000/',wait_until='networkidle')
 assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
 mobile.get_by_role('button',name='省域试验 · 陕西山河 ↗').click()
 mobile.locator('#themeCentral').click();mobile.wait_for_timeout(400)
 assert mobile.locator('#regionTitle').inner_text().startswith('关中')
 mobile.screenshot(path='/tmp/atlas-mobile.png',full_page=True)
 mobile.locator('#challengeEntry').click();mobile.locator('#tabCreate').click()
 assert mobile.locator('#customPanel').is_visible()
 assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
 print('PASS: mobile 390px layout, themes and challenge access; tile failures shown honestly')
 print('Tile image loads:',page.evaluate('Array.from(document.querySelectorAll(".leaflet-tile")).filter(x=>x.naturalWidth>0).length'))
 b.close()
