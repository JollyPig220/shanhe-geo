"""Build small-scale Natural Earth preview assets from verified upstream checkouts.
Usage: PYTHONPATH=/tmp/shanhe-geo-tools python3 scripts/prepare_national_data.py
Requires Pillow, numpy, shapely; preparation only, not application runtime.
"""
import base64,hashlib,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from shapely.geometry import shape,mapping
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1]
V=Path('/tmp/shanhe-natural-earth-vector');R=Path('/tmp/shanhe-natural-earth-raster')
VPIN='ca96624a56bd078437bca8184e78163e5039ad19';RPIN='f04832c819e7a203d159dffe93cd9245332d6b33'
def git(root,path):return subprocess.check_output(['git','-C',str(root),'show','HEAD:'+path])
def sha(b):return hashlib.sha256(b).hexdigest()
for root,pin in [(V,VPIN),(R,RPIN)]:assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD']).decode().strip()==pin
source=git(V,'geojson/ne_10m_admin_1_states_provinces.geojson')
names={'CN-BJ':'北京市','CN-TJ':'天津市','CN-HE':'河北省','CN-SX':'山西省','CN-NM':'内蒙古自治区','CN-LN':'辽宁省','CN-JL':'吉林省','CN-HL':'黑龙江省','CN-SH':'上海市','CN-JS':'江苏省','CN-ZJ':'浙江省','CN-AH':'安徽省','CN-FJ':'福建省','CN-JX':'江西省','CN-SD':'山东省','CN-HA':'河南省','CN-HB':'湖北省','CN-HN':'湖南省','CN-GD':'广东省','CN-GX':'广西壮族自治区','CN-HI':'海南省','CN-CQ':'重庆市','CN-SC':'四川省','CN-GZ':'贵州省','CN-YN':'云南省','CN-XZ':'西藏自治区','CN-SN':'陕西省','CN-GS':'甘肃省','CN-QH':'青海省','CN-NX':'宁夏回族自治区','CN-XJ':'新疆维吾尔自治区','CN-TW':'台湾省','CN-HK':'香港特别行政区','CN-MO':'澳门特别行政区'}
groups={key:[] for key in names}
for f in json.loads(source)['features']:
 a=f['properties'];adm=a.get('adm0_a3')
 if adm not in ['CHN','HKG','MAC','TWN']:continue
 key={'HKG':'CN-HK','MAC':'CN-MO','TWN':'CN-TW'}.get(adm,a.get('iso_3166_2'))
 # Group the upstream Paracel feature with Hainan; no invented connecting geometry.
 if key=='CN-X01~':key='CN-HI'
 assert key in groups,(key,a['name'])
 geometry=shape(f['geometry']);assert geometry.is_valid,(key,'invalid upstream geometry')
 groups[key].append(geometry)
features=[];geometries={}
for key,items in groups.items():
 assert items,key
 geometry=unary_union(items);assert geometry.is_valid and not geometry.is_empty
 geometries[key]=geometry
 p=geometry.representative_point()
 features.append({'type':'Feature','id':key,'properties':{'id':key,'name':names[key],'label':[p.y,p.x],'source_parts':len(items)},'geometry':mapping(geometry)})
for f in features:
 key=f['id'];g=geometries[key]
 # Shared line only: point contacts and sea proximity are not adjacency.
 f['properties']['neighbors']=[other for other in names if other!=key and g.boundary.intersection(geometries[other].boundary).length>1e-7]
collection={'type':'FeatureCollection','features':features}
data=ROOT/'data';data.mkdir(exist_ok=True)
(data/'provinces-preview.geojson').write_text(json.dumps(collection,ensure_ascii=False,separators=(',',':'))+'\n')
# HYP source is EPSG:4326, 1/30 degree pixels, pixel centers from its world file.
# Reproject the image to Web Mercator BEFORE L.imageOverlay (otherwise latitude is distorted).
raw=git(R,'50m_rasters/HYP_50M_SR/HYP_50M_SR.tif')
from io import BytesIO
im=Image.open(BytesIO(raw));assert im.size==(10800,5400)
left,bottom,right,top=65,0,145,60
width=2400;merc_top=np.log(np.tan(np.pi/4+np.deg2rad(top)/2));height=round(width*merc_top/np.deg2rad(right-left))
y=merc_top*(1-(np.arange(height)+.5)/height)
lat=np.rad2deg(2*np.arctan(np.exp(y))-np.pi/2)
source_y=(90-lat)*30-.5
start=np.floor(source_y).astype(int);weight=(source_y-start)[:,None,None]
# Exact 1/30 degree longitudinal crop; bilinear vertical resampling.
a=np.asarray(im)[:,7350:9750,:]
out=(a[start]*(1-weight)+a[start+1]*weight).round().astype('uint8')
Image.fromarray(out).save(data/'china-relief.jpg',quality=91,optimize=True)
(data/'NATURAL_EARTH_LICENSE.md').write_bytes((V/'LICENSE.md').read_bytes())
manifest={'status':'technical-preview-not-standard-map','retrieved_at_utc':'2026-10-19','official_comparison':'Blocked: bzdt.ch.mnr.gov.cn unavailable via current network; boundary currency, territorial completeness and island allocation have NOT been certified. Do not treat this layer as current official administrative or territorial boundaries.','vector':{'publisher':'Natural Earth','repository':'https://github.com/nvkelso/natural-earth-vector','commit':VPIN,'path':'geojson/ne_10m_admin_1_states_provinces.geojson','source_sha256':sha(source),'version':git(V,'10m_cultural/ne_10m_admin_1_states_provinces.VERSION.txt').decode().strip(),'scale':'1:10,000,000','crs':'EPSG:4326','license':'Public domain; upstream LICENSE.md covers raster and vector','effective_boundary_date':None,'positional_accuracy_m':None,'processing':'Select CHN/HKG/MAC/TWN upstream groups; dissolve HKG/MAC/TWN groups; group source Paracel feature with Hainan. Preserve source coordinates, no hand drawing, no simplification, no invented connecting lines. Names normalized. Grouping does not certify official island allocation.','expected_features':34,'source_parts':{k:len(v) for k,v in groups.items()},'neighbors':'Shared source boundary segments only; does not establish complete official adjacency.'},'raster':{'publisher':'Natural Earth','repository':'https://github.com/nvkelso/natural-earth-raster','commit':RPIN,'path':'50m_rasters/HYP_50M_SR/HYP_50M_SR.tif','source_sha256':sha(raw),'version':git(R,'50m_rasters/HYP_50M_SR/HYP_50M_SR.VERSION.txt').decode().strip(),'scale':'1:50,000,000','source_crs':'EPSG:4326','source_cell_degrees':1/30,'output_crs':'EPSG:3857','bounds_latlng':[[bottom,left],[top,right]],'size_px':[width,height],'processing':'Crop 65–145E, 0–60N; bilinear latitude reprojection to Web Mercator; JPEG quality 91; no manual terrain edits. Colors blend climate and elevation; not a numerical elevation classification.','license':'Public domain','effective_terrain_date':None},'outputs':{}}
for path in ['provinces-preview.geojson','china-relief.jpg']:manifest['outputs'][path]={'sha256':sha((data/path).read_bytes()),'bytes':(data/path).stat().st_size}
(data/'sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(manifest['outputs'],indent=2))
