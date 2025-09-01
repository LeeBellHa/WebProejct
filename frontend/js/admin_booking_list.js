document.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem('token');
  if (!token) {
    alert('로그인이 필요합니다.');
    return location.href = 'index.html';
  }

  // 토큰 파싱
  let payload;
  try {
    payload = JSON.parse(atob(token.split('.')[1]));
  } catch {
    localStorage.removeItem('token');
    alert('유효하지 않은 토큰입니다.');
    return location.href = 'index.html';
  }

  // 권한 체크
  if (payload.role !== 'admin') {
    alert('관리자 전용 페이지입니다.');
    return location.href = 'index.html';
  }

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };

  let allBookings = [];

  // ✅ 1) 예약 전체 불러오기 (관리자 전용)
  async function loadBookings() {
    try {
      // 백엔드에서 전체 예약을 반환하도록 구현해둔 엔드포인트 사용
      const res = await fetch('/api/bookings/', { headers }); // 관리자 권한이면 전체 반환하도록 구현
      if (!res.ok) {
        console.error('예약 조회 실패', res.status);
        document.getElementById('bookingBody').innerHTML =
          '<tr><td colspan="4">예약을 불러오는 중 오류가 발생했습니다.</td></tr>';
        return;
      }
      allBookings = await res.json();

      // 날짜+시간 정렬
      allBookings.sort((a, b) => {
        const da = new Date(`${a.start_date}T${a.start_time}`);
        const db = new Date(`${b.start_date}T${b.start_time}`);
        return da - db;
      });

      populateRoomSelect();
      applyFilters();
    } catch (err) {
      console.error('예약 불러오기 실패', err);
      document.getElementById('bookingBody').innerHTML =
        '<tr><td colspan="4">데이터를 불러올 수 없습니다.</td></tr>';
    }
  }

  // ✅ 2) 호실 셀렉트 박스 채우기
  function populateRoomSelect() {
    const select = document.getElementById('roomSelect');
    select.innerHTML = '<option value="">전체 호실</option>';
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

  // ✅ 3) 필터링
  function applyFilters() {
    const term = document.getElementById('searchInput').value.trim().toLowerCase();
    const roomFilter = document.getElementById('roomSelect').value;

    const filtered = allBookings.filter(b => {
      // 🚫 관리자(admin)가 만든 예약(차단 블록)은 제외
      if (b.user?.role === 'admin') return false;

      const uname = (b.user?.username || '').toLowerCase();
      const roomName = b.room?.room_name || `호실 ${b.room_id}`;
      const okName = !term || uname.includes(term);
      const okRoom = !roomFilter || roomName === roomFilter;
      return okName && okRoom;
    });

    renderTable(filtered);
  }


  // ✅ 4) 테이블 렌더링
  function renderTable(list) {
    const tbody = document.getElementById('bookingBody');
    tbody.innerHTML = '';
    if (list.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4">조건에 맞는 예약이 없습니다.</td></tr>';
      return;
    }
    list.forEach(b => {
      const uname = b.user?.username || '—';
      const roomName = b.room?.room_name || `호실 ${b.room_id}`;
      const start = b.start_time.slice(0, 5);
      const end = b.end_time.slice(0, 5);
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${uname}</td>
        <td>${b.start_date}</td>
        <td>${start} ~ ${end}</td>
        <td>${roomName}</td>
      `;
      tbody.append(tr);
    });
  }

  // 이벤트
  document.getElementById('searchInput').addEventListener('input', applyFilters);
  document.getElementById('roomSelect').addEventListener('change', applyFilters);

  // 초기 로드
  loadBookings();
});
