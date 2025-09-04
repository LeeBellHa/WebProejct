// ========== 공통 헬퍼만 추가 ==========
function go(path) {
  const p = path.startsWith('/') ? path : `/${path}`;
  location.assign(p);
}
function api(path) {
  const p = path.startsWith('/') ? path : `/${path}`;
  return new URL(p, location.origin).toString();
}
function readJwt(token) {
  try { return JSON.parse(atob(token.split('.')[1])); } catch { return null; }
}
// =====================================

document.addEventListener('DOMContentLoaded', () => {
  // 🔑 인증 체크
  const token = localStorage.getItem('token');
  if (!token) {
    alert('로그인이 필요합니다.');
    go('/index.html');
    return;
  }
  let payload = readJwt(token);
  if (!payload) {
    localStorage.removeItem('token');
    go('/index.html');
    return;
  }
  if (payload.role !== 'user') {
    alert('사용자 전용 페이지입니다.');
    go('/index.html');
    return;
  }

  const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

  // 로그아웃
  const logoutEl = document.getElementById('logout');
  if (logoutEl) {
    logoutEl.onclick = () => {
      localStorage.removeItem('token');
      go('/index.html');
    };
  }

  // 인사말
  document.getElementById('greeting').textContent = `환영합니다, ${payload.sub || '사용자'}님!`;

  // ───────────── flatpickr 초기화 ─────────────
  function initDatePickerWithPolicy() {
    function nowInKST() {
      const fmt = new Intl.DateTimeFormat('en-CA', {
        timeZone: 'Asia/Seoul',
        year: 'numeric', month: '2-digit', day: '2-digit'
      });
      const parts = Object.fromEntries(fmt.formatToParts(new Date()).map(p => [p.type, p.value]));
      return { y:+parts.year, m:+parts.month, d:+parts.day };
    }
    function addDays(y,m,d,add){
      const dt = new Date(Date.UTC(y,m-1,d));
      dt.setUTCDate(dt.getUTCDate()+add);
      return { y:dt.getUTCFullYear(), m:dt.getUTCMonth()+1, d:dt.getUTCDate() };
    }
    function ymd(y,m,d){ return `${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`; }

    function computeRange() {
      const n = nowInKST();
      const today = ymd(n.y, n.m, n.d); // 오늘 날짜 (KST)

      const weekday = (new Date(Date.UTC(n.y, n.m-1, n.d)).getUTCDay()+6)%7; // 월=0..일=6
      const monThis = addDays(n.y,n.m,n.d,-weekday);
      const sunThis = addDays(monThis.y,monThis.m,monThis.d,6);
      const monNext = addDays(monThis.y,monThis.m,monThis.d,7);
      const sunNext = addDays(sunThis.y,sunThis.m,sunThis.d,7);

      const passedFri9 = (weekday>4)||(weekday===4 && new Date().getHours()>=9);

      // ✅ 최소 날짜는 오늘과 이번 주 월요일 중 더 나중 것
      const min = today > ymd(monThis.y,monThis.m,monThis.d)
        ? today
        : ymd(monThis.y,monThis.m,monThis.d);

      const max = passedFri9
        ? ymd(sunNext.y,sunNext.m,sunNext.d)
        : ymd(sunThis.y,sunThis.m,sunThis.d);

      return { min, max };
    }

    const { min, max } = computeRange();
    flatpickr("#bookingDate", {
      locale: "ko",
      dateFormat: "Y-m-d",
      minDate: min,   // ✅ 오늘 이전은 회색 처리
      maxDate: max,
      defaultDate: min,
      disableMobile: true
    });
  }


  // 실행
  initDatePickerWithPolicy();

  // ───────────── 달력 가드 (이번 주 + 금 09:00 이후 다음 주) ─────────────
  const bookingDate = document.getElementById('bookingDate');

  function nowInKST() {
    const fmt = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Seoul',
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      hour12: false,
    });
    const parts = Object.fromEntries(fmt.formatToParts(new Date()).map(p => [p.type, p.value]));
    return {
      y: +parts.year, m: +parts.month, d: +parts.day,
      hh: +parts.hour, mm: +parts.minute, ss: +parts.second,
    };
  }
  function ymd(y, m, d) {
    return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
  }
  function addDays(y, m, d, add) {
    const dt = new Date(Date.UTC(y, m - 1, d));
    dt.setUTCDate(dt.getUTCDate() + add);
    return { y: dt.getUTCFullYear(), m: dt.getUTCMonth() + 1, d: dt.getUTCDate() };
  }
  function computeBookableRangeKST() {
    const now = nowInKST();
    const todayUTC = new Date(Date.UTC(now.y, now.m - 1, now.d));
    const weekday = (todayUTC.getUTCDay() + 6) % 7; // 월=0...일=6

    const mondayThis = addDays(now.y, now.m, now.d, -weekday);
    const sundayThis = addDays(mondayThis.y, mondayThis.m, mondayThis.d, 6);

    const mondayNext = addDays(mondayThis.y, mondayThis.m, mondayThis.d, 7);
    const sundayNext = addDays(sundayThis.y, sundayThis.m, sundayThis.d, 7);

    const passedFriday9 = (weekday > 4) || (weekday === 4 && now.hh >= 9);

    const minStr = ymd(mondayThis.y, mondayThis.m, mondayThis.d);
    const maxStr = passedFriday9
      ? ymd(sundayNext.y, sundayNext.m, sundayNext.d)
      : ymd(sundayThis.y, sundayThis.m, sundayThis.d);

    return { minStr, maxStr };
  }
  function clampDate(value, minStr, maxStr) {
    if (!value) return minStr;
    if (value < minStr) return minStr;
    if (value > maxStr) return maxStr;
    return value;
  }
  function applyDatePolicy() {
    const { minStr, maxStr } = computeBookableRangeKST();
    bookingDate.min = minStr;
    bookingDate.max = maxStr;
    bookingDate.value = clampDate(bookingDate.value, minStr, maxStr);
    return { minStr, maxStr };
  }

  // 초기 적용
  let lastRange = applyDatePolicy();

  // 변경 가드
  bookingDate.addEventListener('change', () => {
    const { minStr, maxStr } = lastRange || computeBookableRangeKST();
    const v = clampDate(bookingDate.value, minStr, maxStr);
    if (v !== bookingDate.value) {
      alert(`해당 날짜는 예약할 수 없습니다.\n가능한 기간: ${minStr} ~ ${maxStr}`);
      bookingDate.value = v;
      bookingDate.dispatchEvent(new Event('input'));
    }
  });
  // 직접 타이핑 방지
  bookingDate.addEventListener('keydown', (e) => {
    const allow = ['Tab', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Backspace', 'Delete'];
    if (!allow.includes(e.key)) e.preventDefault();
  });
  // 금 09:00 이후 자동 확장
  setInterval(() => {
    const { minStr, maxStr } = computeBookableRangeKST();
    if (!lastRange || minStr !== lastRange.minStr || maxStr !== lastRange.maxStr) {
      lastRange = { minStr, maxStr };
      bookingDate.min = minStr;
      bookingDate.max = maxStr;
      bookingDate.value = clampDate(bookingDate.value, minStr, maxStr);
    }
  }, 60 * 1000);

  // ───────────── 격자 상태 ─────────────
  const grid = document.getElementById('grid');
  const gridWrapper = document.getElementById('gridWrapper');
  const rows = 30, cols = 30;
  let currentFloor = 1;
  let floors = [1];
  let filledCells = {};
  let stickers = [];
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
      const res = await fetch(api('/api/cells/'), { headers });
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
      const res = await fetch(api('/api/rooms/'), { headers });
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
    const { minStr, maxStr } = computeBookableRangeKST();
    if (date < minStr || date > maxStr) {
      alert(`해당 날짜는 예약할 수 없습니다.\n가능한 기간: ${minStr} ~ ${maxStr}`);
      bookingDate.value = clampDate(date, minStr, maxStr);
      return;
    }

    try {
      const res = await fetch(api(`/api/rooms/${selectedRoomId}/slots?booking_date=${date}`), { headers });
      if (!res.ok) throw new Error('슬롯 불러오기 실패');
      const slots = await res.json();
      slotsContainer.innerHTML = '';
      selectedSlots = [];

      slots.forEach(slot => {
        const btn = document.createElement('button');
        btn.textContent = `${slot.start.split('T')[1].substring(0, 5)}~${slot.end.split('T')[1].substring(0, 5)}`;
        btn.className = 'slot ' + (slot.available ? 'available' : 'unavailable');
        btn.disabled = !slot.available;
        if (slot.available) {
          btn.onclick = () => {
            const idx = selectedSlots.findIndex(s => s.start === slot.start && s.end === slot.end);
            if (idx >= 0) {
              selectedSlots.splice(idx, 1);
              btn.classList.remove('selected');
            } else {
              if (selectedSlots.length >= 4) {
                alert('최대 2시간까지만 선택할 수 있습니다.');
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

    const sorted = [...selectedSlots].sort((a, b) => new Date(a.start) - new Date(b.start));
    const firstSlot = sorted[0];
    const lastSlot = sorted[sorted.length - 1];

    const date = bookingDate.value;

    try {
      const res = await fetch(api('/api/bookings/'), {
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
        const err = await res.json().catch(() => ({}));
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
