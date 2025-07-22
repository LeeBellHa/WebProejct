// admin.js
document.addEventListener('DOMContentLoaded', () => {
  // 1) 사이드바 토글
  const toggle = document.getElementById('menuToggle');
  toggle.addEventListener('click', () => {
    document.body.classList.toggle('collapsed');
  });

  // 2) 인증 체크
  const token = localStorage.getItem('token');
  if (!token) {
    alert('관리자 로그인 후 접근하세요.');
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
  if (payload.role !== 'admin') {
    alert('관리자만 접근 가능합니다.');
    return location.href = 'index.html';
  }

  // 3) 전역 헤더
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
  document.getElementById('logout').addEventListener('click', () => {
    localStorage.removeItem('token');
    location.href = 'index.html';
  });

  // 4) 데이터 로딩 함수들
  async function loadPending() {
    const res = await fetch('/users/pending', { headers });
    if (!res.ok) return;
    const list = await res.json();
    const tbody = document.querySelector('#pendingTable tbody');
    tbody.innerHTML = '';
    if (list.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty">승인 대기 중인 사용자가 없습니다.</td></tr>';
      return;
    }
    list.forEach(u => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${u.login_id}</td>
        <td>${u.username}</td>
        <td>${u.student_id}</td>
        <td>${u.major}</td>
        <td>${u.phone}</td>
        <td class="actions">
          <button class="approve">승인</button>
          <button class="delete">삭제</button>
        </td>
      `;
      tr.querySelector('.approve').onclick = async () => {
        await fetch(`/users/${u.user_id}/approve`, { method: 'PATCH', headers });
        loadAll();
      };
      tr.querySelector('.delete').onclick = async () => {
        if (!confirm('정말 이 사용자를 삭제하시겠습니까?')) return;
        await fetch(`/users/${u.user_id}`, { method: 'DELETE', headers });
        loadAll();
      };
      tbody.appendChild(tr);
    });
  }

  async function loadUsers() {
    const res = await fetch('/users', { headers });
    if (!res.ok) return;
    const list = await res.json();
    const normals = list.filter(u => u.role === 'user');
    const tbody = document.querySelector('#userTable tbody');
    tbody.innerHTML = '';
    if (normals.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="empty">등록된 일반 사용자가 없습니다.</td></tr>';
      return;
    }
    normals.forEach(u => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${u.login_id}</td>
        <td class="password-cell">
          <button class="toggle-pw">보기</button>
          <span class="plain" style="display:none;">${u.password}</span>
        </td>
        <td>${u.username}</td>
        <td>${u.student_id}</td>
        <td>${u.major}</td>
        <td>${u.phone}</td>
        <td class="actions">
          <button class="delete">삭제</button>
        </td>
      `;
      tr.querySelector('.toggle-pw').onclick = () => {
        const span = tr.querySelector('.plain');
        const btn  = tr.querySelector('.toggle-pw');
        if (span.style.display === 'none') {
          span.style.display = '';
          btn.textContent    = '가리기';
        } else {
          span.style.display = 'none';
          btn.textContent    = '보기';
        }
      };
      tr.querySelector('.delete').onclick = async () => {
        if (!confirm('정말 이 사용자를 삭제하시겠습니까?')) return;
        await fetch(`/users/${u.user_id}`, { method: 'DELETE', headers });
        loadAll();
      };
      tbody.appendChild(tr);
    });
  }

  // 5) 전체 로드
  function loadAll() {
    loadPending();
    loadUsers();
  }
  loadAll();
});
