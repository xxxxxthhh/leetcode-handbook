/* 错题登记：localStorage 存本地，不上传任何地方。
   localStorage 不可用（隐私模式 / file:// 限制）时整个表单降级隐藏，
   页面仍然是一张可以打印出来手写的空白表格。 */
(function () {
  var KEY = 'alg-threshold-mistakes';
  var form = document.getElementById('log-form');
  var tbody = document.getElementById('log-body');
  var empty = document.getElementById('log-empty');
  if (!form || !tbody) return;

  function available() {
    try {
      localStorage.setItem(KEY + '-probe', '1');
      localStorage.removeItem(KEY + '-probe');
      return true;
    } catch (e) {
      return false;
    }
  }

  if (!available()) {
    form.style.display = 'none';
    var warn = document.getElementById('log-unavailable');
    if (warn) warn.hidden = false;
    return;
  }

  function load() {
    try {
      return JSON.parse(localStorage.getItem(KEY)) || [];
    } catch (e) {
      return [];
    }
  }

  function save(rows) {
    localStorage.setItem(KEY, JSON.stringify(rows));
  }

  function render() {
    var rows = load();
    tbody.innerHTML = '';
    if (empty) empty.hidden = rows.length > 0;
    // 空白行只在屏幕上让位给真实记录；打印时由 CSS 强制显示回来
    var blank = document.getElementById('log-blank');
    if (blank) blank.hidden = rows.length > 0;
    rows.forEach(function (r, i) {
      var tr = document.createElement('tr');
      [r.num, r.pattern, r.why, r.redo].forEach(function (v) {
        var td = document.createElement('td');
        td.textContent = v || '—';       // textContent 而非 innerHTML：登记内容不当 HTML 解析
        tr.appendChild(td);
      });
      var td = document.createElement('td');
      var del = document.createElement('button');
      del.type = 'button';
      del.className = 'btn ghost';
      del.textContent = '删除';
      del.addEventListener('click', function () {
        var cur = load();
        cur.splice(i, 1);
        save(cur);
        render();
      });
      td.appendChild(del);
      tr.appendChild(td);
      tbody.appendChild(tr);
    });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var data = new FormData(form);
    var num = (data.get('num') || '').trim();
    if (!num) return;
    var rows = load();
    rows.push({
      num: num,
      pattern: data.get('pattern') || '',
      why: (data.get('why') || '').trim(),
      redo: data.get('redo') || ''
    });
    save(rows);
    form.reset();
    render();
  });

  var clear = document.getElementById('log-clear');
  if (clear) {
    clear.addEventListener('click', function () {
      if (!load().length) return;
      if (window.confirm('清空全部错题记录？此操作不可撤销。')) {
        localStorage.removeItem(KEY);
        render();
      }
    });
  }

  render();
})();
