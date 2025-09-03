// // 회원가입 요청 보내기
// document.addEventListener('DOMContentLoaded', () => {
//   const form = document.getElementById('regForm');
//   const result = document.getElementById('result');

//   form.addEventListener('submit', async e => {
//     e.preventDefault();
//     const data = {
//       login_id:   form.login_id.value,
//       password:   form.password.value,
//       username:   form.username.value,
//       student_id: form.student_id.value,
//       major:      form.major.value,
//       phone:      form.phone.value || null
//     };

//     try {
//       const res = await fetch('/users/register', {
//         method:  'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body:    JSON.stringify(data),
//       });
//       const json = await res.json();
//       result.textContent = JSON.stringify(json, null, 2);
//     } catch (err) {
//       result.textContent = err;
//     }
//   });
// });


// 클라이언트 유효성 검사 + 제출
(function () {
  const form = document.getElementById('regForm');
  const result = document.getElementById('result');
  const consentCheckbox = document.getElementById('consentRequired');

  // 패턴(백엔드에서도 동일 검증 권장)
  const patterns = {
    login_id: /^[A-Za-z~!@#$%^&*()_+\-={}\[\]|\\:;'",.<>/?`]+$/,
    password: /^[A-Za-z~!@#$%^&*()_+\-={}\[\]|\\:;'",.<>/?`]+$/,
    username: /^[A-Za-z\uAC00-\uD7A3\s]+$/,
    student_id: /^\d{8}$/,
    phone: /^010-\d{4}-\d{4}$/ // 선택값
  };

  function showMsg(msg, ok = false) {
    result.textContent = msg;
    result.style.color = ok ? '#0b7a0b' : '#b00020';
  }

  function validate() {
    const data = Object.fromEntries(new FormData(form));
    // 필수값 체크
    if (!data.login_id || !data.password || !data.username || !data.student_id || !data.major) {
      showMsg('필수 항목을 모두 입력하세요.');
      return false;
    }
    // 패턴 체크
    if (!patterns.login_id.test(data.login_id)) {
      showMsg('Login ID는 영문/특수문자만 가능합니다. (숫자 불가)');
      return false;
    }
    if (!patterns.password.test(data.password) || data.password.length < 8) {
      showMsg('Password는 영문/특수문자만 가능하며 8자 이상이어야 합니다. (숫자 불가)');
      return false;
    }
    if (!patterns.username.test(data.username)) {
      showMsg('이름은 한글 또는 영문만 입력 가능합니다.');
      return false;
    }
    if (!patterns.student_id.test(data.student_id)) {
      showMsg('학번은 숫자 8자리여야 합니다.');
      return false;
    }
    if (data.phone && !patterns.phone.test(data.phone)) {
      showMsg('전화번호 형식이 올바르지 않습니다. 예) 010-1234-5678');
      return false;
    }
    if (!consentCheckbox.checked) {
      showMsg('개인정보 수집 및 이용에 동의가 필요합니다.');
      return false;
    }
    return true;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    result.textContent = '';

    if (!validate()) return;

    const payload = Object.fromEntries(new FormData(form));
    // 백엔드 API 엔드포인트는 기존 것 사용(예: /api/auth/register)
    try {
      // CSRF/토큰 등은 서버 정책에 맞춰 적용
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        credentials: 'include'
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.message || `회원가입 실패 (HTTP ${res.status})`);
      }

      const data = await res.json().catch(() => ({}));
      showMsg('회원가입 신청이 완료되었습니다. 관리자 승인 후 로그인 가능합니다.', true);

      // 필요 시 폼 초기화
      form.reset();
      // 동의 체크박스도 초기화됨
    } catch (err) {
      showMsg(err.message || '네트워크 오류가 발생했습니다.');
    }
  });
})();
