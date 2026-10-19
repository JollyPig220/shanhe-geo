from playwright.sync_api import sync_playwright
from pathlib import Path
import subprocess,re,json
root=Path(__file__).resolve().parents[1]
old=subprocess.check_output(['git','show','6ddc0ce:index.html'],cwd=root).decode()
rows=json.loads(re.search(r'const mountains=(\[.*?\])\.map',old)[1].replace("'",'"'))
new=json.loads((root/'data/mountains.js').read_text().split('const mountainQuestions = ')[1].rstrip(';\n'))
assert [[q[k] for k in ['name','lat','lng','info']] for q in new]==rows
assert len(new)==12 and all(q['radius']==135 for q in new)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.add_init_script('''if(!localStorage.getItem('shanhe_total')){localStorage.setItem('shanhe_total','9');localStorage.setItem('shanhe_custom','[{"name":"已有题","lat":34,"lng":108}]');localStorage.setItem('shanhe_wrong','[{"name":"旧错题","lat":30,"lng":100}]')}''')
 page.goto('http://127.0.0.1:8000/',wait_until='networkidle')
 page.locator('#challengeEntry').click();page.locator('#mountainPickerSummary').click()
 assert page.locator('#mountainChoices input:checked').count()==12
 page.locator('[data-mountain-group=basic]').click()
 assert page.locator('#mountainChoices input:checked').count()==6
 assert page.evaluate('order.length')==12
 page.locator('#startMountainSelection').click()
 assert page.evaluate('order.length')==6
 assert page.evaluate('order.every(q=>q.level==="basic")')
 # Answer a current target on its actual coordinate through Leaflet's click event.
 page.evaluate('map.fire("click",{latlng:L.latLng(order[0].lat,order[0].lng)})')
 assert page.evaluate('correct')==1 and page.evaluate('total')==10
 page.locator('[data-mountain-group=none]').click()
 assert page.locator('#startMountainSelection').is_disabled()
 page.get_by_role('button',name='重新开始本专题').click()
 assert page.evaluate('correct')==1 and page.evaluate('order.length')==6
 page.locator('[data-mountain-group=advanced]').click()
 page.locator('#startMountainSelection').click()
 assert page.evaluate('order.length')==6 and page.evaluate('order.every(q=>q.level==="advanced")')
 page.locator('[data-mountain-group=none]').click()
 page.get_by_label('祁连山',exact=True).check()
 page.locator('#startMountainSelection').click()
 assert page.evaluate('order.length')==1 and page.evaluate('order[0].name')=='祁连山'
 page.evaluate('map.fire("click",{latlng:L.latLng(0,0)})')
 assert page.evaluate('incorrect')==1
 assert page.evaluate('wrong.some(q=>q.name==="祁连山")')
 page.locator('#nextBtn').click()
 assert page.locator('#feedback').inner_text().startswith('完成！')
 page.locator('#setSelect').select_option('rivers')
 assert not page.locator('#mountainPicker').is_visible()
 assert page.evaluate('order.length')==9
 page.locator('#setSelect').select_option('wrong')
 assert page.evaluate('order.some(q=>q.name==="旧错题")')
 page.locator('#setSelect').select_option('mountains')
 assert page.evaluate('order.length')==1
 assert page.evaluate('customs[0].name')=='已有题'
 page.screenshot(path='/tmp/mountain-selection-desktop.png',full_page=True)
 page.reload(wait_until='networkidle')
 assert page.evaluate('total')==11
 assert page.evaluate('wrong.some(q=>q.name==="旧错题")')
 assert page.evaluate('customs[0].name')=='已有题'
 assert not errors,errors
 mobile=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 mobile.goto('http://127.0.0.1:8000/',wait_until='networkidle');mobile.locator('#challengeEntry').click();mobile.locator('#mountainPickerSummary').click()
 assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
 mobile.locator('[data-mountain-group=basic]').click();mobile.locator('#startMountainSelection').click()
 assert mobile.evaluate('order.length')==6
 mobile.screenshot(path='/tmp/mountain-selection-mobile.png',full_page=True)
 b.close()
print('PASS: exact original 12 points retained; grouping, individual choices, empty selection guard, deferred start, right/wrong feedback, wrong set, old storage, other sets, mobile layout; no JS errors')
