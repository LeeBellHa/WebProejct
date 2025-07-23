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

  // 상태
  let floors = [1];
  let currentFloor = 1;
  const rows = 30, cols = 30;
  let cells = {};      // { floor: Set("x,y") }
  let stickers = [];   // [{ room_name, floor, x, y }]
  let drawMode = 'view';
  let isMouseDown = false;

  const grid = document.getElementById('grid');
  const penBtn = document.getElementById('penMode');
  const eraserBtn = document.getElementById('eraserMode');
  const addStickerBtn = document.getElementById('addSticker');
  const saveBtn = document.getElementById('saveButton');
  const floorContainer = document.getElementById('floorButtons');
  const gridWrapper = document.getElementById('gridWrapper');

  // 층 버튼 렌더
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

  // 격자 렌더
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

  // 스티커 렌더
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
    document.addEventListener('mouseup', () => {
      if (dragging) {
        dragging = false;
        data.x = parseInt(div.style.left);
        data.y = parseInt(div.style.top);
      }
    });
    div.addEventListener('input', () => {
      data.room_name = div.textContent.trim();
    });
    div.addEventListener('dblclick', () => {
      if (confirm('스티커 삭제?')) {
        const idx = stickers.indexOf(data);
        if (idx > -1) {
          stickers.splice(idx, 1);
          renderStickers();
        }
      }
    });

    return div;
  }

  // 모드 토글
  penBtn.onclick = () => {
    if (drawMode === 'pen') {
      drawMode = 'view';
      penBtn.classList.remove('active');
    } else {
      drawMode = 'pen';
      penBtn.classList.add('active');
      eraserBtn.classList.remove('active');
    }
  };
  eraserBtn.onclick = () => {
    if (drawMode === 'eraser') {
      drawMode = 'view';
      eraserBtn.classList.remove('active');
    } else {
      drawMode = 'eraser';
      eraserBtn.classList.add('active');
      penBtn.classList.remove('active');
    }
  };

  addStickerBtn.onclick = () => {
    stickers.push({ room_name: '새 연습실', floor: currentFloor, x: 0, y: 0 });
    renderStickers();
  };

  // 💾 저장 버튼: rooms + cells 저장
  saveBtn.onclick = async () => {
    try {
      // 1) 스티커(rooms) 저장
      for (const s of stickers) {
        await fetch('/api/rooms/', {
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
      }
      // 2) cells 저장 (층별 반복)
      // 기존 데이터 초기화를 원한다면 DELETE 먼저
      await fetch('/api/cells/', { method: 'DELETE', headers });

      // 모든 층 데이터 모으기
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

  // ✅ DB에서 기존 방 목록 불러오기
  async function loadRooms() {
    try {
      const res = await fetch('/api/rooms/', { headers });
      if (!res.ok) throw new Error('방 불러오기 실패');
      const data = await res.json();
      stickers = data.map(room => ({
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

  // ✅ DB에서 기존 cell 목록 불러오기
  async function loadCells() {
    try {
      const res = await fetch('/api/cells/', { headers });
      if (!res.ok) throw new Error('셀 불러오기 실패');
      const data = await res.json();
      // 층별로 셋 구성
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
  loadCells(); // ✅ 격자 데이터도 로드
});
