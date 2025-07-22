// js/user.js
document.addEventListener('DOMContentLoaded', () => {
  // ── 네비/인증 ────────────────────────────
  const toggle = document.getElementById('menuToggle');
  toggle.addEventListener('click', () =>
    document.body.classList.toggle('collapsed')
  );

  const token = localStorage.getItem('token');
  if (!token) {
    alert('로그인이 필요합니다.');
    return location.href = 'index.html';
  }
  let payload;
  try {
    payload = JSON.parse(atob(token.split('.')[1]));
  } catch {
    localStorage.removeItem('token');
    alert('유효하지 않은 토큰입니다.');
    return location.href = 'index.html';
  }
  if (payload.role !== 'user') {
    alert('접근 권한이 없습니다.');
    return location.href = 'index.html';
  }

  const username = payload.username || payload.sub || '사용자';
  document.getElementById('greeting').textContent = `환영합니다, ${username}님!`;
  document.getElementById('logout').addEventListener('click', () => {
    localStorage.removeItem('token');
    location.href = 'index.html';
  });

  // ── 예약 로직 ────────────────────────────
  const API_BASE = '/api';
  let selectedSlots = [];

  const modal      = document.getElementById('slotModal');
  const backdrop   = modal.querySelector('.modal-backdrop');
  const closeBtn   = document.getElementById('closeModal');
  const slotsWrap  = document.getElementById('slotsContainer');
  const confirmBtn = document.getElementById('confirmBooking');

  // 1) 연습실 목록 불러오기
  async function loadRooms() {
    try {
      const res = await fetch(`${API_BASE}/rooms/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('방 목록 조회 실패');
      const rooms = await res.json();
      const select = document.getElementById('roomSelect');
      select.innerHTML = '<option value="" disabled selected>연습실을 선택하세요</option>';
      rooms.forEach(r => {
        const opt = document.createElement('option');
        opt.value = r.room_id;
        opt.textContent = r.room_name;
        select.appendChild(opt);
      });
    } catch (err) {
      console.error(err);
      alert('연습실 목록을 불러오는 중 오류가 발생했습니다.');
    }
  }

  // 2) 예약 가능 주(min/max) 설정
  function setDateInputRange() {
    const now = new Date(
      new Date().toLocaleString('en-US', { timeZone: 'Asia/Seoul' })
    );
    const wd = now.getDay(); // 일=0 … 토=6
    const daysToFri = (5 - wd + 7) % 7;
    const fri = new Date(now);
    fri.setDate(now.getDate() + daysToFri);
    fri.setHours(9, 0, 0, 0);

    let start = new Date(fri);
    if (now >= fri) {
      start.setDate(fri.getDate() + 3); // 다음 주 월
    } else {
      start.setDate(fri.getDate() - 4); // 이번 주 월
    }
    const end = new Date(start);
    end.setDate(start.getDate() + 6);

    const inp = document.getElementById('bookingDate');
    inp.min = start.toISOString().slice(0, 10);
    inp.max = end.toISOString().slice(0, 10);
  }

  // 3) 시간표 불러오기 (모달 오픈 포함)
  async function loadSlots() {
    selectedSlots = [];
    const roomId = +document.getElementById('roomSelect').value;
    const date   = document.getElementById('bookingDate').value;
    if (!roomId || !date) {
      return alert('연습실과 날짜를 모두 선택해주세요.');
    }
    try {
      const res = await fetch(
        `${API_BASE}/rooms/${roomId}/slots?booking_date=${date}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      if (!res.ok) throw new Error('시간표 조회 실패');
      const slots = await res.json();
      renderSlots(slots);
      openModal();
    } catch (err) {
      console.error(err);
      alert('시간표를 불러오는 중 오류가 발생했습니다.');
    }
  }

  function openModal() {
    modal.classList.remove('hidden');
  }
  function closeModal() {
    modal.classList.add('hidden');
    selectedSlots = [];
    slotsWrap.querySelectorAll('.selected')
      .forEach(el => el.classList.remove('selected'));
  }

  backdrop.addEventListener('click', closeModal);
  closeBtn.addEventListener('click', closeModal);

  // 4) 슬롯 렌더링
  function renderSlots(slots) {
    slotsWrap.innerHTML = '';
    slots.forEach(s => {
      const div = document.createElement('div');
      div.classList.add('slot', s.available ? 'available' : 'unavailable');

      const start = new Date(s.start)
        .toLocaleTimeString('ko-KR', { hour:'2-digit', minute:'2-digit' });
      const end = new Date(s.end)
        .toLocaleTimeString('ko-KR', { hour:'2-digit', minute:'2-digit' });
      div.textContent = `${start} – ${end}`;

      if (s.available) {
        div.addEventListener('click', () => toggleSlotSelection(div, s));
      }
      slotsWrap.appendChild(div);
    });
    updateReserveButtonState();
  }

  // 5) 슬롯 선택/해제
  function toggleSlotSelection(div, slot) {
    const idx = selectedSlots.findIndex(x => x.start === slot.start && x.end === slot.end);
    if (idx >= 0) {
      selectedSlots.splice(idx, 1);
      div.classList.remove('selected');
    } else {
      const temp = [...selectedSlots, slot]
        .sort((a, b) => new Date(a.start) - new Date(b.start));
      const duration = (new Date(temp.at(-1).end) - new Date(temp[0].start)) / 60000;
      if (duration > 120) {
        return alert('최대 연속 2시간까지만 예약할 수 있습니다.');
      }
      selectedSlots.push(slot);
      div.classList.add('selected');
    }
    updateReserveButtonState();
  }

  // 6) 예약 버튼 활성/비활성
  function updateReserveButtonState() {
    confirmBtn.disabled = selectedSlots.length === 0;
  }

  // 7) 예약 확정
  async function confirmBooking() {
    if (!selectedSlots.length) return;
    const sorted = [...selectedSlots].sort((a, b) => new Date(a.start) - new Date(b.start));
    const roomId = +document.getElementById('roomSelect').value;
    const date   = document.getElementById('bookingDate').value;
    const payloadBody = {
      room_id:    roomId,
      start_date: date,
      end_date:   date,
      start_time: sorted[0].start.split('T')[1],
      end_time:   sorted.at(-1).end.split('T')[1]
    };

    try {
      const res = await fetch(`${API_BASE}/bookings/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payloadBody)
      });
      if (!res.ok) {
        const e = await res.json();
        throw new Error(e.detail || res.statusText);
      }
      alert('예약이 완료되었습니다.');
      loadSlots();
      closeModal();
    } catch (err) {
      console.error(err);
      alert('예약 실패: ' + err.message);
    }
  }

  // ── 초기화 호출 ──────────────────────────
  loadRooms();
  setDateInputRange();
  document.getElementById('loadSlots').addEventListener('click', loadSlots);
  confirmBtn.addEventListener('click', confirmBooking);
});
