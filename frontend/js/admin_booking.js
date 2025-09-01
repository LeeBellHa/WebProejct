// 공지/예약 차단 관리 로직
document.addEventListener('DOMContentLoaded', () => {
  // --- Auth & headers ---
  const token = localStorage.getItem('token');
  const headers = { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };

  // 요소들
  const noticeForm      = document.getElementById('notice-form');
  const titleInput      = document.getElementById('notice-title-input');
  const contentInput    = document.getElementById('notice-input');
  const submitBtn       = document.getElementById('notice-submit-btn');
  const cancelBtn       = document.getElementById('cancel-edit-btn');
  const deleteBtn       = document.getElementById('delete-notice-btn');
  const noticeIdInput   = document.getElementById('notice-id');
  const noticeList      = document.getElementById('notice-list');

  const roomSelect      = document.getElementById('room-select');
  const blockForm       = document.getElementById('block-form');
  const blockTableBody  = document.querySelector('#block-table tbody');

  let isEditingNotice = false;
  const roomsMap = {};

  // === 공지 CRUD ===
  async function loadNotices() {
    const res = await fetch('/api/notices', { headers });
    if (!res.ok) return alert('공지 로딩 실패');
    const list = await res.json();
    noticeList.innerHTML = '';
    list.forEach(n => {
      const li = document.createElement('li');
      li.textContent = `[${n.created_at.split('T')[0]}] ${n.title}`;
      li.onclick = () => startEdit(n);
      noticeList.appendChild(li);
    });
  }
  function startEdit(n) {
    isEditingNotice = true;
    noticeIdInput.value = n.notice_id;
    titleInput.value    = n.title;
    contentInput.value  = n.content;
    submitBtn.textContent = '수정 완료';
    cancelBtn.classList.remove('hidden');
    deleteBtn.classList.remove('hidden');
  }
  function resetNoticeForm() {
    isEditingNotice = false;
    noticeForm.reset();
    noticeIdInput.value = '';
    submitBtn.textContent = '공지 올리기';
    cancelBtn.classList.add('hidden');
    deleteBtn.classList.add('hidden');
  }
  noticeForm.addEventListener('submit', async e => {
    e.preventDefault();
    const title = titleInput.value.trim();
    const content = contentInput.value.trim();
    if (!title || !content) return alert('제목과 내용을 모두 입력하세요.');

    const url = isEditingNotice
      ? `/api/admin/notices/${noticeIdInput.value}`
      : '/api/admin/notices';
    const method = isEditingNotice ? 'PATCH' : 'POST';

    try {
      const res = await fetch(url, {
        method, headers,
        body: JSON.stringify({ title, content })
      });
      if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
      resetNoticeForm();
      await loadNotices();
      alert(isEditingNotice ? '공지 수정 완료' : '공지 작성 완료');
    } catch (err) {
      console.error(err);
      alert((isEditingNotice ? '수정' : '작성') + ' 실패: ' + err.message);
    }
  });
  cancelBtn.onclick = resetNoticeForm;
  deleteBtn.onclick = async () => {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    try {
      const res = await fetch(
        `/api/admin/notices/${noticeIdInput.value}`,
        { method: 'DELETE', headers }
      );
      if (res.status !== 204) throw new Error((await res.json()).detail || res.statusText);
      resetNoticeForm();
      await loadNotices();
      alert('공지 삭제 완료');
    } catch (err) {
      console.error(err);
      alert('삭제 실패: ' + err.message);
    }
  };

  // === 연습실 로딩 ===
  async function loadRooms() {
    const res = await fetch('/api/rooms/', { headers });
    if (!res.ok) return alert('연습실 로딩 실패');
    const rooms = await res.json();
    roomSelect.innerHTML = '<option value="">-- 선택 --</option>';
    rooms.forEach(r => {
      roomsMap[r.room_id] = r.room_name;
      const opt = document.createElement('option');
      opt.value = r.room_id;
      opt.textContent = r.room_name;
      roomSelect.appendChild(opt);
    });
  }

  // === 블록 관리 ===
  async function loadBlocks() {
    const res = await fetch('/api/admin/bookings/', { headers });
    if (!res.ok) return alert('블록 로딩 실패');
    const list = await res.json();
    blockTableBody.innerHTML = '';
    list.forEach(b => {
      const period = (b.start_date === b.end_date)
        ? b.start_date
        : `${b.start_date} ~ ${b.end_date}`;
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${b.booking_id}</td>
        <td>${b.room?.room_name || roomsMap[b.room_id] || b.room_id}</td>
        <td>${period}</td>
        <td>${b.start_time}</td>
        <td>${b.end_time}</td>
        <td><button class="btn-del">삭제</button></td>
      `;

      // ✅ confirm 없이 바로 삭제 & 행 제거
      tr.querySelector('.btn-del').onclick = async () => {
        try {
          const res = await fetch(`/api/admin/bookings/${b.booking_id}`, {
            method: 'DELETE', headers
          });
          if (res.status === 204) {
            tr.remove(); // 성공 시 행만 제거
          } else {
            const err = await res.json().catch(() => ({}));
            alert(err.detail || '삭제 실패');
          }
        } catch (err) {
          console.error(err);
          alert('삭제 요청 실패');
        }
      };

      blockTableBody.appendChild(tr);
    });
  }

  blockForm.addEventListener('submit', async e => {
    e.preventDefault();
    const room_id    = +roomSelect.value;
    const start_date = document.getElementById('start-date-input').value;
    const end_date   = document.getElementById('end-date-input').value;
    if (!room_id || !start_date || !end_date) {
      return alert('모든 필드를 입력해주세요.');
    }
    try {
      await fetch('/api/admin/bookings/', {
        method: 'POST', headers,
        body: JSON.stringify({
          room_id, start_date, end_date,
          start_time:'00:00:00', end_time:'23:59:59'
        })
      });
      alert('블록 생성 완료');
      loadBlocks();
    } catch (err) {
      console.error(err);
      alert('블록 생성 실패');
    }
  });

  // === 초기 로드 ===
  loadNotices();
  loadRooms().then(loadBlocks); // roomsMap 준비 후 블록 불러오기
});
