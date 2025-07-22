// admin_booking_list.js
document.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem('token');
  if (!token) {
    alert('로그인이 필요합니다.');
    return location.href = 'index.html';
  }

  // 토큰 페이로드 확인 (admin/user 접근)
  let payload;
  try {
    payload = JSON.parse(atob(token.split('.')[1]));
  } catch {
    localStorage.removeItem('token');
    alert('유효하지 않은 토큰입니다.');
    return location.href = 'index.html';
  }
  if (!['admin','user'].includes(payload.role)) {
    alert('권한 오류');
    return location.href = 'index.html';
  }

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };

  let allBookings = [];

  // 1) 예약 불러오기
  async function loadBookings() {
    const url = (payload.role === 'admin')
      ? '/api/bookings/'
      : '/api/bookings/me';
    const res = await fetch(url, { headers });
    if (!res.ok) {
      console.error('예약 조회 실패', res.status);
      document.getElementById('bookingBody').innerHTML =
        '<tr><td colspan="4">예약을 불러오는 중 오류가 발생했습니다.</td></tr>';
      return;
    }
    allBookings = await res.json();
    // 날짜+시간으로 정렬
    allBookings.sort((a, b) => {
      const da = new Date(`${a.start_date}T${a.start_time}`);
      const db = new Date(`${b.start_date}T${b.start_time}`);
      return da - db;
    });
    populateRoomSelect();
    applyFilters();
  }

  // 2) 호실 셀렉트 박스 채우기
  function populateRoomSelect() {
    const select = document.getElementById('roomSelect');
    // 고유 호실명 추출
    const rooms = Array.from(new Set(
      allBookings.map(b => b.room?.room_name || `호실 ${b.room_id}`)
    )).sort((a, b) => a.localeCompare(b, 'ko'));
    rooms.forEach(name => {
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name;
      select.append(opt);
    });
  }

  // 3) 필터 & 렌더링
  function applyFilters() {
    const term = document.getElementById('searchInput').value.trim().toLowerCase();
    const roomFilter = document.getElementById('roomSelect').value;
    const filtered = allBookings.filter(b => {
      const uname = (b.user?.username || '').toLowerCase();
      const roomName = b.room?.room_name || `호실 ${b.room_id}`;
      const okName = !term || uname.includes(term);
      const okRoom = !roomFilter || roomName === roomFilter;
      return okName && okRoom;
    });
    renderTable(filtered);
  }

  function renderTable(list) {
    const tbody = document.getElementById('bookingBody');
    tbody.innerHTML = '';
    if (list.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4">조건에 맞는 예약이 없습니다.</td></tr>';
      return;
    }
    list.forEach(b => {
      const name = b.user?.username || '—';
      const roomName = b.room?.room_name || `호실 ${b.room_id}`;
      const start = b.start_time.slice(0,5);
      const end   = b.end_time.slice(0,5);
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${name}</td>
        <td>${b.start_date}</td>
        <td>${start} – ${end}</td>
        <td>${roomName}</td>
      `;
      tbody.append(tr);
    });
  }

  // 이벤트 바인딩
  document.getElementById('searchInput')
    .addEventListener('input', applyFilters);
  document.getElementById('roomSelect')
    .addEventListener('change', applyFilters);

  // 초기 로드
  loadBookings();
});
