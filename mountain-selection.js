/* The picker only supplies a set; the existing quiz still shuffles and scores it. */
function createMountainSelection(questions, onStart) {
  const selected = new Set(questions.map(q => q.id));
  const host = document.getElementById('mountainChoices');
  const status = document.getElementById('mountainSelectionStatus');
  function renderState() {
    host.querySelectorAll('input').forEach(input => { input.checked=selected.has(input.value); });
    document.getElementById('mountainPickerSummary').textContent='选择山脉 · 已选 '+selected.size+' / '+questions.length;
    document.getElementById('startMountainSelection').disabled=selected.size===0;
    status.textContent=selected.size ? '已勾选 '+selected.size+' 题。开始或重新开始时应用，并重置本轮进度。' : '请至少选择一座山脉；当前练习不会被清空。';
  }
  for(const [level,title] of [['basic','基础'],['advanced','进阶']]) {
    const fieldset=document.createElement('fieldset');
    const legend=document.createElement('legend');legend.textContent=title;
    const list=document.createElement('div');list.className='mountain-checks';
    for(const question of questions.filter(q=>q.level===level)) {
      const label=document.createElement('label');
      const input=document.createElement('input');input.type='checkbox';input.value=question.id;
      input.addEventListener('change',()=>{if(input.checked)selected.add(question.id);else selected.delete(question.id);renderState();});
      label.append(input,document.createTextNode(question.name));list.append(label);
    }
    fieldset.append(legend,list);host.append(fieldset);
  }
  document.querySelectorAll('[data-mountain-group]').forEach(button=>button.addEventListener('click',()=>{
    const group=button.dataset.mountainGroup;selected.clear();
    questions.filter(q=>group==='all'||q.level===group).forEach(q=>selected.add(q.id));
    renderState();
  }));
  document.getElementById('startMountainSelection').addEventListener('click',()=>{if(selected.size)onStart();});
  renderState();
  return {
    getSelected:()=>questions.filter(q=>selected.has(q.id)),
    canStart:()=>selected.size>0,
    setVisible(show) {
      document.getElementById('mountainPicker').classList.toggle('hidden',!show);
      document.getElementById('mountainPointNotice').classList.toggle('hidden',!show);
    }
  };
}
