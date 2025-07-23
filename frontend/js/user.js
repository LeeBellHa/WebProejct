document.addEventListener('DOMContentLoaded', () => {
  // 🔑 인증 체크
  const token = localStorage.getItem('token');
  if (!token) {
    alert('로그인이 필요합니다.');
    location.href = 'index.html';
    return;
  }
  let payload;
  try {
    payload = JSON.parse(atob(token.split('.')[1]));
  } catch {
    localStorage.removeItem('token');
    location.href = 'index.html';
    return;
  }
  if (payload.role !== 'user') {
    alert('사용자 전용 페이지입니다.');
    location.href = 'index.html';
    return;
  }

  const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

  // 로그아웃
  document.getElementById('logout').onclick = () => {
    localStorage.removeItem('token');
    location.href = 'index.html';
  };

  // 인사말
  document.getElementById('greeting').textContent = `환영합니다, ${payload.sub || '사용자'}님!`;

  // ───────────── 격자 상태 ─────────────
  const grid = document.getElementById('grid');
  const gridWrapper = document.getElementById('gridWrapper');
  const rows = 30, cols = 30;
  let currentFloor = 1;
  let floors = [1];
  let filledCells = {}; // { floor: Set("x,y") }
  let stickers = []; // [{room_id, room_name, floor, x, y}]
  let selectedRoomId = null;

  function renderGrid() {
    grid.innerHTML = '';
    grid.style.gridTemplateColumns = `repeat(${cols}, 20px)`;
    grid.style.gridTemplateRows = `repeat(${rows}, 20px)`;
    if (!filledCells[currentFloor]) filledCells[currentFloor] = new Set();
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        if (filledCells[currentFloor].has(`${x},${y}`)) {
          cell.classList.add('filled');
        }
        grid.appendChild(cell);
      }
    }
    renderStickers();
  }

  function renderStickers() {
    document.querySelectorAll('.sticker').forEach(e => e.remove());
    stickers.filter(s => s.floor === currentFloor).forEach(s => {
      const div = document.createElement('div');
      div.className = 'sticker';
      if (s.room_id === selectedRoomId) div.classList.add('selected');
      div.textContent = s.room_name;
      div.style.left = s.x + 'px';
      div.style.top = s.y + 'px';
      div.onclick = () => {
        selectedRoomId = s.room_id;
        renderStickers();
      };
      gridWrapper.appendChild(div);
    });
  }

  function renderFloorButtons() {
    const floorContainer = document.getElementById('floorButtons');
    floorContainer.innerHTML = '';
    floors.forEach(f => {
      const btn = document.createElement('button');
      btn.textContent = `${f}층`;
      if (f === currentFloor) btn.classList.add('active-floor');
      btn.onclick = () => {
        currentFloor = f;
        renderFloorButtons();
        renderGrid();
      };
      floorContainer.appendChild(btn);
    });
  }

  async function loadCells() {
    try {
      const res = await fetch('/api/cells/', { headers });
      if (!res.ok) throw new Error('셀 불러오기 실패');
      const data = await res.json();
      filledCells = {};
      floors = [1];
      data.forEach(c => {
        if (!filledCells[c.floor]) filledCells[c.floor] = new Set();
        filledCells[c.floor].add(`${c.x},${c.y}`);
        if (!floors.includes(c.floor)) floors.push(c.floor);
      });
      renderFloorButtons();
      renderGrid();
    } catch (err) {
      console.error(err);
      alert('연습실 배치 데이터를 불러올 수 없습니다.');
    }
  }

  async function loadRooms() {
    try {
      const res = await fetch('/api/rooms/', { headers });
      if (!res.ok) throw new Error('방 목록 불러오기 실패');
      const rooms = await res.json();
      stickers = rooms.map(r => ({
        room_id: r.room_id,
        room_name: r.room_name,
        floor: r.floor,
        x: r.pos_x,
        y: r.pos_y
      }));
      renderStickers();
    } catch (err) {
      console.error(err);
      alert('방 목록을 불러올 수 없습니다.');
    }
  }

  // ───────────── 시간표/예약 ─────────────
  const bookingDate = document.getElementById('bookingDate');
  const loadSlotsBtn = document.getElementById('loadSlots');
  const slotsContainer = document.getElementById('slotsContainer');
  const slotModal = document.getElementById('slotModal');
  const closeModal = document.getElementById('closeModal');
  const confirmBooking = document.getElementById('confirmBooking');
  let selectedSlots = [];

  loadSlotsBtn.onclick = async () => {
    if (!selectedRoomId) {
      alert('연습실을 선택해 주세요.');
      return;
    }
    const date = bookingDate.value;
    if (!date) {
      alert('날짜를 선택해 주세요.');
      return;
    }
    try {
      const res = await fetch(`/api/rooms/${selectedRoomId}/slots?booking_date=${date}`, { headers });
      if (!res.ok) throw new Error('슬롯 불러오기 실패');
      const slots = await res.json();
      slotsContainer.innerHTML = '';
      selectedSlots = []; // 초기화

      slots.forEach(slot => {
        const btn = document.createElement('button');
        btn.textContent = `${slot.start.split('T')[1].substring(0,5)}~${slot.end.split('T')[1].substring(0,5)}`;
        btn.className = 'slot ' + (slot.available ? 'available' : 'unavailable');
        btn.disabled = !slot.available;
        if (slot.available) {
          btn.onclick = () => {
            const idx = selectedSlots.findIndex(s => s.start === slot.start && s.end === slot.end);
            if (idx >= 0) {
              // 이미 선택된 슬롯 → 해제
              selectedSlots.splice(idx, 1);
              btn.classList.remove('selected');
            } else {
              // 새로 선택하려는 경우
              if (selectedSlots.length >= 4) {
                alert('최대 2시간 까지만 선택할 수 있습니다.');
                return;
              }
              selectedSlots.push(slot);
              btn.classList.add('selected');
            }
            confirmBooking.disabled = selectedSlots.length === 0;
          };
        }
        slotsContainer.appendChild(btn);
      });
      slotModal.classList.remove('hidden');
    } catch (err) {
      console.error(err);
      alert('시간표를 불러오지 못했습니다.');
    }
  };

  closeModal.onclick = () => {
    slotModal.classList.add('hidden');
    selectedSlots = [];
    confirmBooking.disabled = true;
    document.querySelectorAll('#slotsContainer .slot').forEach(b => b.classList.remove('selected'));
  };

  
  confirmBooking.onclick = async () => {
    if (selectedSlots.length === 0) return;

    // 선택된 슬롯들을 시간 순으로 정렬
    const sorted = [...selectedSlots].sort((a, b) => new Date(a.start) - new Date(b.start));
    const firstSlot = sorted[0];
    const lastSlot = sorted[sorted.length - 1];

    // 같은 날짜라는 전제로 동작
    const date = bookingDate.value;

    try {
      const res = await fetch('/api/bookings/', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          room_id: selectedRoomId,
          start_date: date,
          end_date: date,
          start_time: firstSlot.start.split('T')[1],
          end_time: lastSlot.end.split('T')[1]
        })
      });
      if (!res.ok) {
        const err = await res.json();
        alert(err.detail || '예약 실패');
        return;
      }
      alert('예약 완료!');
      slotModal.classList.add('hidden');
      confirmBooking.disabled = true;
      selectedSlots = [];
    } catch (err) {
      console.error(err);
      alert('예약 실패');
    }
  };


  // 초기 로딩
  loadCells();
  loadRooms();
});
