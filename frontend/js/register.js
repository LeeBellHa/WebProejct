// 회원가입 요청 보내기
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('regForm');
  const result = document.getElementById('result');

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const data = {
      login_id:   form.login_id.value,
      password:   form.password.value,
      username:   form.username.value,
      student_id: form.student_id.value,
      major:      form.major.value,
      phone:      form.phone.value || null
    };

    try {
      const res = await fetch('/users/register', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(data),
      });
      const json = await res.json();
      result.textContent = JSON.stringify(json, null, 2);
    } catch (err) {
      result.textContent = err;
    }
  });
});
