/* Small-scale display layers. Future terrain units, mountains and water systems
   register here as independent layers, not quiz datasets. */
function createNationalAtlas(map) {
  const layerRegistry = new Map();
  const featureLayers = new Map();
  const featureIndex = new Map();
  const labels = L.layerGroup();
  const labelEntries = [];
  const bounds = L.latLngBounds([[3, 73], [54, 136]]);
  const baseStyle = {color: '#48594d', weight: 1.05, opacity: .8, fillColor: '#e7dcad', fillOpacity: .025};
  let selected = null, visible = false, ready = false, loading = null;
  const relief = L.imageOverlay('data/china-relief.jpg', [[0,65],[60,145]], {
    attribution: '地形与省界资料：<a href="https://www.naturalearthdata.com/">Natural Earth</a> · Public domain',
    interactive: false
  });
  relief.on('error', () => {
    document.getElementById('mapStatus').classList.remove('hidden');
    document.getElementById('mapStatusText').textContent = '本地地形图片加载失败，请刷新页面重试。';
  });
  const provinces = L.geoJSON(null, {
    style: baseStyle,
    onEachFeature(feature, layer) {
      const p = feature.properties;
      featureLayers.set(p.id, layer);
      featureIndex.set(p.id, feature);
      layer.bindTooltip(p.name, {sticky:true, direction:'top'});
      layer.on('click', e => { L.DomEvent.stopPropagation(e); selectProvince(p.id); });
      layer.on('mouseover', () => { if(selected !== p.id) layer.setStyle({weight:2, fillOpacity:.12}); });
      layer.on('mouseout', () => { if(selected !== p.id) layer.setStyle(baseStyle); });
      const shortName = p.name.replace(/壮族自治区|回族自治区|维吾尔自治区|自治区|特别行政区|省|市/g, '');
      const marker = L.marker(p.label, {
        icon:L.divIcon({className:'province-name'+(['CN-HK','CN-MO','CN-TJ','CN-SH'].includes(p.id)?' compact-name':''), html:shortName, iconSize:[76,20], iconAnchor:[38,10]}),
        keyboard:false, interactive:false
      });
      labels.addLayer(marker);
      labelEntries.push({marker, text:shortName, compact:['CN-HK','CN-MO','CN-TJ','CN-SH'].includes(p.id), priority:layer.getBounds().getNorthEast().distanceTo(layer.getBounds().getSouthWest())});
    }
  });
  layerRegistry.set('provinces', provinces);
  layerRegistry.set('province-labels', labels);
  function avoidLabelOverlap() {
    const occupied=[];
    for(const entry of [...labelEntries].sort((a,b)=>b.priority-a.priority)) {
      const element=entry.marker.getElement();if(!element)continue;
      const p=map.latLngToContainerPoint(entry.marker.getLatLng());
      const half=entry.text.length*6+4;
      const rect={left:p.x-half,right:p.x+half,top:p.y-13,bottom:p.y+13};
      const hidden=(entry.compact&&map.getZoom()<6)||occupied.some(r=>rect.left<r.right&&rect.right>r.left&&rect.top<r.bottom&&rect.bottom>r.top);
      element.classList.toggle('label-collided',hidden);
      if(!hidden)occupied.push(rect);
    }
  }
  map.on('moveend zoomend resize',avoidLabelOverlap);
  function sync() {
    for(const [id, layer] of layerRegistry) {
      const input = document.querySelector('[data-map-layer="'+id+'"]');
      const show = visible && (input ? input.checked : false);
      if(show && !map.hasLayer(layer)) map.addLayer(layer);
      if(!show && map.hasLayer(layer)) map.removeLayer(layer);
    }
    avoidLabelOverlap();
  }
  function registerLayer(id, layer) {
    if(layerRegistry.has(id)) throw new Error('Duplicate map layer: '+id);
    layerRegistry.set(id, layer);
    sync();
  }
  function selectProvince(id, focus=false) {
    const feature = featureIndex.get(id), layer = featureLayers.get(id);
    if(!feature || !layer) return;
    if(selected) featureLayers.get(selected).setStyle(baseStyle);
    selected = id;
    layer.setStyle({color:'#9b5b2f', weight:2.4, opacity:1, fillColor:'#d2a85e', fillOpacity:.24});
    layer.bringToFront();
    const p = feature.properties;
    document.getElementById('provinceSelect').value = id;
    document.getElementById('provinceTitle').textContent = p.name;
    document.getElementById('provinceDescription').textContent = '已高亮资料中的轮廓。对照地形观察它的位置、形状，以及与周围省区的关系。';
    const neighborHost = document.getElementById('provinceNeighbors');
    neighborHost.replaceChildren();
    for(const neighbor of p.neighbors) {
      const button = document.createElement('button');
      button.type='button';button.textContent=featureIndex.get(neighbor).properties.name;
      button.onclick=()=>selectProvince(neighbor);
      neighborHost.append(button);
    }
    document.getElementById('neighborNote').textContent = p.neighbors.length ? '资料中共享陆地边线的省区（不含隔海关系）' : '此资料未识别出共享陆地边线；不代表没有空间联系。';
    document.getElementById('provinceDetail').classList.remove('hidden');
    document.getElementById('enterShaanxi').classList.toggle('hidden',id!=='CN-SN');
    document.getElementById('focusProvince').disabled=false;
    if(focus) focusSelected();
  }
  function clearSelection() {
    if(selected) featureLayers.get(selected).setStyle(baseStyle);
    selected=null;
    document.getElementById('provinceSelect').value='';
    document.getElementById('provinceTitle').textContent='从全国，看见彼此';
    document.getElementById('provinceDescription').textContent='点击地图中的省区，或从目录选择。先辨认轮廓，再沿着省界观察相邻关系。';
    document.getElementById('provinceDetail').classList.add('hidden');
    document.getElementById('enterShaanxi').classList.add('hidden');
    document.getElementById('focusProvince').disabled=true;
  }
  function focusSelected() {
    if(!selected) return;
    map.fitBounds(featureLayers.get(selected).getBounds(), {padding:[35,65],maxZoom:8,animate:false});
  }
  async function load() {
    if(ready) return;
    if(loading) return loading;
    document.getElementById('provinceLoadState').textContent='正在载入省区资料…';
    loading=(async()=>{
      try {
        const response=await fetch('data/provinces-preview.geojson');
        if(!response.ok) throw new Error('HTTP '+response.status);
        const data=await response.json();
        if(data.type!=='FeatureCollection'||data.features.length!==34||new Set(data.features.map(f=>f.properties.id)).size!==34) throw new Error('Province dataset failed validation');
        provinces.addData(data);
        const select=document.getElementById('provinceSelect');
        for(const feature of data.features) {
          const option=document.createElement('option');option.value=feature.properties.id;option.textContent=feature.properties.name;select.append(option);
        }
        select.disabled=false;ready=true;
        document.getElementById('provinceLoadState').textContent='34 个省级目录 · 小比例尺资料预览';
        document.getElementById('retryProvinces').classList.add('hidden');
        sync();
      } catch(error) {
        console.error('Province data load failed',error);
        document.getElementById('provinceLoadState').textContent='省界资料加载失败，地形仍可浏览。';
        document.getElementById('retryProvinces').classList.remove('hidden');
      } finally { loading=null; }
    })();
    return loading;
  }
  document.querySelectorAll('[data-map-layer]').forEach(input=>input.addEventListener('change',sync));
  document.getElementById('provinceSelect').addEventListener('change',e=>e.target.value?selectProvince(e.target.value):clearSelection());
  document.getElementById('focusProvince').onclick=focusSelected;
  document.getElementById('clearProvince').onclick=clearSelection;
  document.getElementById('retryProvinces').onclick=load;
  map.on('zoomend',()=>document.getElementById('map').classList.toggle('show-compact-names',map.getZoom()>=6));
  return {
    relief, bounds, load, selectProvince, registerLayer,
    setVisible(value) {visible=value;sync();},
    reset() {clearSelection();map.fitBounds(bounds,{padding:[4,50],animate:false});},
    get ready(){return ready;},
    get selected(){return selected;},
    get layerIds(){return Array.from(layerRegistry.keys());}
  };
}
