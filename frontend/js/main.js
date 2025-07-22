// 1) 공지사항 불러오기
async function loadPublicNotices() {
  try {
    const res = await fetch('/api/notices');
    if (!res.ok) return;
    const list = await res.json();
    const ul = document.getElementById('public-notice-list');
    ul.innerHTML = '';
    list.forEach(n => {
      const li = document.createElement('li');
      if (n.is_urgent) li.classList.add('urgent');
      li.innerHTML = `
        [${n.created_at.split('T')[0]}]
        <a href="notice.html?id=${n.notice_id}">${n.title}</a>
      `;
      ul.appendChild(li);
    });
  } catch (err) {
    console.error('공지 로딩 실패', err);
  }
}

// 2) 로그인 처리
async function handleLogin(e) {
  e.preventDefault();
  const form = e.target;
  const data = new URLSearchParams({
    username: form.login_id.value,
    password: form.password.value
  });
  const res = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: data
  });
  if (!res.ok) {
    const err = await res.json();
    return alert(err.detail || "로그인 실패");
  }
  const { access_token, role } = await res.json();
  if (role === "pending") {
    return alert("아직 승인 대기 중인 계정입니다.");
  }
  localStorage.setItem("token", access_token);
  location.href = role === "admin" ? "admin_userlist.html" : "user.html";
}

// 3) 이벤트 바인딩
document.addEventListener("DOMContentLoaded", () => {
  loadPublicNotices();
  document.getElementById("loginForm")
          .addEventListener("submit", handleLogin);
  document.getElementById("goRegister")
          .addEventListener("click", () => location.href = "register.html");
});

