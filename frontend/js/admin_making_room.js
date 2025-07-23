document.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem('token');
  if (!token) { alert('로그인 필요'); location.href = 'index.html'; return; }

  let payload;
  try { payload = JSON.parse(atob(token.split('.')[1])); }
  catch { localStorage.removeItem('token'); location.href = 'index.html'; return; }
  if (payload.role !== 'admin') {
    alert('관리자만 접근 가능합니다.');
    location.href = 'index.html'; return;
  }

  const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };
  document.getElementById('logout').onclick = () => {
    localStorage.removeItem('token');
    location.href = 'index.html';
  };

  // 상태값
  let floors = [1];
  let currentFloor = 1;
  const rows = 30, cols = 30;
  let cells = {}; // { floor:Set("x,y") }
  let stickers = []; // [{ room_id, room_name, floor, x, y }]
  let drawMode = 'view';
  let isMouseDown = false;

  // ✅ copy/paste용 버퍼
  let copyBuffer = null;

  // 요소
  const grid = document.getElementById('grid');
  const gridWrapper = document.getElementById('gridWrapper');
  const floorContainer = document.getElementById('floorButtons');
  const penBtn = document.getElementById('penMode');
  const eraserBtn = document.getElementById('eraserMode');
  const addStickerBtn = document.getElementById('addSticker');
  const saveBtn = document.getElementById('saveButton');
  const copyBtn = document.getElementById('copyCells');
  const pasteBtn = document.getElementById('pasteCells');

  function renderFloors() {
    floorContainer.innerHTML = '';
    floors.forEach(f => {
      const b = document.createElement('button');
      b.textContent = f + '층';
      if (f === currentFloor) b.classList.add('active-floor');
      b.onclick = () => { currentFloor = f; renderFloors(); renderGrid(); renderStickers(); };
      floorContainer.appendChild(b);
    });
    const add = document.createElement('button');
    add.textContent = '+';
    add.onclick = () => {
      const next = Math.max(...floors) + 1;
      floors.push(next);
      currentFloor = next;
      renderFloors(); renderGrid(); renderStickers();
    };
    floorContainer.appendChild(add);
  }

  function renderGrid() {
    grid.innerHTML = '';
    if (!cells[currentFloor]) cells[currentFloor] = new Set();
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        if (cells[currentFloor].has(`${x},${y}`)) cell.classList.add('filled');

        cell.addEventListener('mousedown', () => {
          if (drawMode === 'pen') {
            isMouseDown = true;
            cells[currentFloor].add(`${x},${y}`);
            cell.classList.add('filled');
          } else if (drawMode === 'eraser') {
            isMouseDown = true;
            cells[currentFloor].delete(`${x},${y}`);
            cell.classList.remove('filled');
          }
        });
        cell.addEventListener('mouseenter', () => {
          if (!isMouseDown) return;
          if (drawMode === 'pen') {
            cells[currentFloor].add(`${x},${y}`);
            cell.classList.add('filled');
          } else if (drawMode === 'eraser') {
            cells[currentFloor].delete(`${x},${y}`);
            cell.classList.remove('filled');
          }
        });

        grid.appendChild(cell);
      }
    }
  }
  document.addEventListener('mouseup', () => { isMouseDown = false; });

  function renderStickers() {
    document.querySelectorAll('.sticker').forEach(el => el.remove());
    stickers.filter(s => s.floor === currentFloor).forEach(s => {
      const div = createStickerDiv(s);
      gridWrapper.appendChild(div);
    });
  }

  function createStickerDiv(data) {
    const div = document.createElement('div');
    div.className = 'sticker';
    div.contentEditable = true;
    div.textContent = data.room_name;
    div.style.left = data.x + 'px';
    div.style.top = data.y + 'px';

    let dragging = false, ox = 0, oy = 0;
    div.addEventListener('mousedown', e => {
      if (drawMode !== 'view') return;
      dragging = true;
      ox = e.offsetX;
      oy = e.offsetY;
      e.stopPropagation();
    });
    document.addEventListener('mousemove', e => {
      if (dragging) {
        div.style.left = (e.pageX - gridWrapper.offsetLeft - ox) + 'px';
        div.style.top = (e.pageY - gridWrapper.offsetTop - oy) + 'px';
      }
    });
    document.addEventListener('mouseup', async () => {
      if (dragging) {
        dragging = false;
        data.x = parseInt(div.style.left);
        data.y = parseInt(div.style.top);
        if (data.room_id) {
          try {
            await fetch(`/api/rooms/${data.room_id}`, {
              method: 'PATCH',
              headers,
              body: JSON.stringify({ pos_x: data.x, pos_y: data.y })
            });
          } catch (e) { console.error('방 위치 업데이트 실패', e); }
        }
      }
    });

    div.addEventListener('input', async () => {
      data.room_name = div.textContent.trim();
      if (data.room_id) {
        try {
          await fetch(`/api/rooms/${data.room_id}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ room_name: data.room_name })
          });
        } catch (e) { console.error('방 이름 수정 실패', e); }
      }
    });

    div.addEventListener('dblclick', async () => {
      if (confirm('스티커(방)를 삭제하시겠습니까?')) {
        if (data.room_id) {
          try {
            await fetch(`/api/rooms/${data.room_id}`, {
              method: 'DELETE',
              headers
            });
          } catch (e) { console.error('방 삭제 실패', e); }
        }
        const idx = stickers.indexOf(data);
        if (idx > -1) {
          stickers.splice(idx, 1);
          renderStickers();
        }
      }
    });

    return div;
  }

  penBtn.onclick = () => {
    if (drawMode === 'pen') {
      drawMode = 'view'; penBtn.classList.remove('active');
    } else {
      drawMode = 'pen'; penBtn.classList.add('active'); eraserBtn.classList.remove('active');
    }
  };
  eraserBtn.onclick = () => {
    if (drawMode === 'eraser') {
      drawMode = 'view'; eraserBtn.classList.remove('active');
    } else {
      drawMode = 'eraser'; eraserBtn.classList.add('active'); penBtn.classList.remove('active');
    }
  };

  addStickerBtn.onclick = () => {
    stickers.push({ room_id: null, room_name: '새 연습실', floor: currentFloor, x: 0, y: 0 });
    renderStickers();
  };

  // ✅ copy/paste 핸들러
  copyBtn.onclick = () => {
    if (!cells[currentFloor] || cells[currentFloor].size === 0) {
      alert('복사할 셀이 없습니다.');
      return;
    }
    copyBuffer = Array.from(cells[currentFloor]);
    alert(`✅ ${currentFloor}층의 ${copyBuffer.length}개 셀을 복사했습니다.`);
  };

  pasteBtn.onclick = () => {
    if (!copyBuffer || copyBuffer.length === 0) {
      alert('붙여넣을 셀이 없습니다. 먼저 Copy를 눌러주세요.');
      return;
    }
    if (!cells[currentFloor]) cells[currentFloor] = new Set();
    copyBuffer.forEach(coord => cells[currentFloor].add(coord));
    renderGrid();
    alert(`📌 ${currentFloor}층에 ${copyBuffer.length}개의 셀을 붙여넣었습니다.`);
  };

  saveBtn.onclick = async () => {
    try {
      // rooms 저장
      for (const s of stickers) {
        if (!s.room_id) {
          const res = await fetch('/api/rooms/', {
            method: 'POST',
            headers,
            body: JSON.stringify({
              room_name: s.room_name,
              floor: s.floor,
              pos_x: s.x,
              pos_y: s.y,
              state: true,
              equipment: ''
            })
          });
          if (res.ok) {
            const saved = await res.json();
            s.room_id = saved.room_id;
          }
        }
      }

      // cells 저장
      await fetch('/api/cells/', { method: 'DELETE', headers });
      let allCells = [];
      Object.entries(cells).forEach(([floor, set]) => {
        set.forEach(str => {
          const [x, y] = str.split(',').map(Number);
          allCells.push({ floor: Number(floor), x, y });
        });
      });
      if (allCells.length > 0) {
        await fetch('/api/cells/bulk', {
          method: 'POST',
          headers,
          body: JSON.stringify({ cells: allCells })
        });
      }

      alert('저장 완료!');
    } catch (e) {
      console.error(e);
      alert('저장 실패');
    }
  };

  async function loadRooms() {
    try {
      const res = await fetch(`/api/rooms/?_t=${Date.now()}`, { headers, cache: 'no-store' });
      if (!res.ok) throw new Error('방 불러오기 실패');
      const data = await res.json();
      stickers = data.map(room => ({
        room_id: room.room_id,
        room_name: room.room_name,
        floor: room.floor,
        x: room.pos_x,
        y: room.pos_y
      }));
      renderStickers();
    } catch (err) {
      console.error('방 불러오기 오류:', err);
    }
  }

  async function loadCells() {
    try {
      const res = await fetch(`/api/cells/?_t=${Date.now()}`, { headers, cache: 'no-store' });
      if (!res.ok) throw new Error('셀 불러오기 실패');
      const data = await res.json();
      cells = {};
      data.forEach(c => {
        if (!cells[c.floor]) cells[c.floor] = new Set();
        cells[c.floor].add(`${c.x},${c.y}`);
        if (!floors.includes(c.floor)) floors.push(c.floor);
      });
      renderFloors();
      renderGrid();
    } catch (err) {
      console.error('셀 불러오기 오류:', err);
    }
  }

  // 초기 렌더
  renderFloors();
  renderGrid();
  renderStickers();
  loadRooms();
  loadCells();
});
