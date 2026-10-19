"""Run against the real static server on port 8000. No mocked map geometry."""
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'],headless=True)
 page=b.new_page(viewport={'width':1440,'height':1000})
 errors=[];external=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:external.append(r.url) if not r.url.startswith('http://127.0.0.1:8000/') else None)
 existing=[{'name':'原有地点','lat':34.3,'lng':108.9,'info':'保留测试','radius':75}]
 page.add_init_script('if(!localStorage.getItem("shanhe_custom")){localStorage.setItem("shanhe_custom",'+json.dumps(json.dumps(existing,ensure_ascii=False)) +');localStorage.setItem("shanhe_total","7")}')
 page.goto('http://127.0.0.1:8000/',wait_until='networkidle')
 page.wait_for_function('nationalAtlas.ready')
 assert not external,external
 assert page.locator('#explorePanel').is_visible() and not page.locator('#shaanxiPanel').is_visible()
 assert not page.locator('#challengePanel').is_visible()
 assert page.locator('#provinceSelect option').count()==35
 assert page.locator('.leaflet-image-layer').evaluate('(im)=>im.complete&&im.naturalWidth===2400')
 assert page.evaluate('map.getBounds().contains(nationalAtlas.bounds)')
 assert page.evaluate('customs[0].name')=='原有地点' and page.evaluate('total')==7
 # Actual pointer event on a known point in Shaanxi, not an injected select call.
 point=page.evaluate('map.latLngToContainerPoint([35,109])')
 page.locator('#map').click(position={'x':point['x'],'y':point['y']})
 assert page.locator('#provinceTitle').inner_text()=='陕西省'
 assert page.locator('path[stroke="#9b5b2f"]').count()>0
 assert page.locator('#provinceNeighbors button').count()>=6
 page.locator('#provinceNeighbors').get_by_role('button',name='河南省',exact=True).click()
 assert page.locator('#provinceTitle').inner_text()=='河南省'
 for code,name in [('CN-HK','香港特别行政区'),('CN-MO','澳门特别行政区'),('CN-TW','台湾省')]:
  page.locator('#provinceSelect').select_option(code)
  assert page.locator('#provinceTitle').inner_text()==name
  page.locator('#focusProvince').click()
  assert page.evaluate('nationalAtlas.selected')==code
  assert page.evaluate('map.getZoom()')<=8
 page.get_by_role('button',name='全国视野',exact=True).click()
 assert page.evaluate('nationalAtlas.selected') is None
 assert page.evaluate('map.getBounds().contains(nationalAtlas.bounds)')
 page.locator('[data-map-layer="provinces"]').uncheck()
 assert page.locator('.leaflet-overlay-pane path').count()==0
 page.locator('[data-map-layer="province-labels"]').uncheck()
 assert page.locator('.province-name').count()==0
 page.locator('[data-map-layer="provinces"]').check()
 page.locator('[data-map-layer="province-labels"]').check()
 zoom=page.evaluate('map.getZoom()')
 page.locator('.leaflet-control-zoom-in').click();page.wait_for_timeout(400)
 assert page.evaluate('map.getZoom()')>zoom
 center=page.evaluate('map.getCenter().lng')
 box=page.locator('#map').bounding_box()
 page.mouse.move(box['x']+450,box['y']+350);page.mouse.down();page.mouse.move(box['x']+550,box['y']+350,steps=12);page.mouse.up();page.wait_for_timeout(500)
 assert abs(page.evaluate('map.getCenter().lng')-center)>.5
 page.get_by_role('button',name='全国视野',exact=True).click()
 page.screenshot(path='/tmp/national-desktop.png',full_page=True)
 page.locator('#provinceSelect').select_option('CN-SN');page.locator('#enterShaanxi').click()
 assert page.locator('#shaanxiPanel').is_visible()
 assert page.locator('.province-name').count()==0
 page.locator('#themeSouth').click()
 assert page.locator('#regionTitle').inner_text().startswith('陕南')
 page.locator('#challengeEntry').click();page.locator('#tabCreate').click()
 assert page.locator('#customList').inner_text().startswith('原有地点')
 page.reload(wait_until='networkidle');page.wait_for_function('nationalAtlas.ready')
 assert page.evaluate('customs[0].name')=='原有地点'
 assert not errors,errors
 print('PASS: real local relief decode, no external homepage requests, 34 selectors, real map click/highlight, adjacency, HK/MO/TW focus, independent layers, pan/zoom, national reset, Shaanxi access and old storage preservation')
 for width in [390,800]:
  mobile=b.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True)
  mobile.goto('http://127.0.0.1:8000/',wait_until='networkidle');mobile.wait_for_function('nationalAtlas.ready')
  assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert mobile.evaluate('map.getBounds().contains(nationalAtlas.bounds)')
  assert mobile.evaluate('map.getZoom()')>=3
  mobile.locator('#provinceSelect').select_option('CN-MO');mobile.locator('#focusProvince').click()
  assert mobile.locator('#provinceTitle').inner_text()=='澳门特别行政区'
  mobile.get_by_role('button',name='全国视野',exact=True).click()
  if width==390:mobile.screenshot(path='/tmp/national-mobile.png',full_page=True)
 print('PASS: mobile/touch emulation at 390px and 800px, no overflow, complete overview and small-region selection')
 failed=b.new_page()
 failed.route('**/provinces-preview.geojson',lambda route:route.fulfill(status=503,body='Unavailable'))
 failed.goto('http://127.0.0.1:8000/',wait_until='networkidle')
 assert failed.locator('#retryProvinces').is_visible()
 assert failed.locator('#provinceSelect').is_disabled()
 assert failed.locator('.leaflet-image-layer').evaluate('(im)=>im.complete&&im.naturalWidth>0')
 failed.unroute('**/provinces-preview.geojson')
 failed.locator('#retryProvinces').click();failed.wait_for_function('nationalAtlas.ready')
 assert failed.locator('#provinceSelect option').count()==35
 print('PASS: failed province request keeps real terrain usable; retry restores complete dataset')
 b.close()
