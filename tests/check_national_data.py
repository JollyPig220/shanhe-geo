"""Validate the delivered data contract, provenance and current integrity."""
import hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'data/sources.json').read_text())
assert manifest['status']=='technical-preview-not-standard-map'
assert manifest['vector']['effective_boundary_date'] is None
assert manifest['vector']['positional_accuracy_m'] is None
for name,record in manifest['outputs'].items():
 data=(ROOT/'data'/name).read_bytes()
 assert hashlib.sha256(data).hexdigest()==record['sha256'],name
 assert len(data)==record['bytes']
collection=json.loads((ROOT/'data/provinces-preview.geojson').read_text())
features=collection['features'];ids={f['id'] for f in features}
assert len(features)==len(ids)==34
assert {'CN-TW','CN-HK','CN-MO','CN-SN','CN-XJ','CN-XZ','CN-HI'}<=ids
names={f['properties']['name'] for f in features};assert len(names)==34
byid={f['id']:f for f in features}
for f in features:
 p=f['properties'];g=f['geometry']
 assert p['id']==f['id'] and p['source_parts']>=1
 assert set(p['neighbors'])<=ids and p['id'] not in p['neighbors']
 for neighbor in p['neighbors']:assert p['id'] in byid[neighbor]['properties']['neighbors']
 assert g['type'] in ['Polygon','MultiPolygon']
 polygons=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
 for polygon in polygons:
  for ring in polygon:
   assert ring[0]==ring[-1] and len(ring)>=4
   for lon,lat in ring:assert math.isfinite(lon) and math.isfinite(lat) and 65<=lon<=145 and 0<=lat<=60
assert byid['CN-HK']['properties']['source_parts']==18
assert byid['CN-TW']['properties']['source_parts']==21
assert byid['CN-HI']['properties']['source_parts']==2
assert 'CN-HA' in byid['CN-SN']['properties']['neighbors']
print('PASS: 34 unique named features, coordinate/ring contract, source grouping, symmetric adjacency, delivered SHA-256 hashes and explicit unverified accuracy/date')
