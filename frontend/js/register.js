(function () {
  const form = document.getElementById('regForm');
  const result = document.getElementById('result');
  const consentCheckbox = document.getElementById('consentRequired');

  // 정규식 패턴
  const patterns = {
    login_id: /^[A-Za-z0-9~!@#$%^&*()_+\-={}\[\]|\\:;'",.<>/?`]+$/,
    password: /^[A-Za-z0-9~!@#$%^&*()_+\-={}\[\]|\\:;'",.<>/?`]+$/,
    username: /^[A-Za-z\uAC00-\uD7A3\s]+$/,
    student_id: /^\d{8}$/,
    phone: /^010-\d{4}-\d{4}$/
  };

  // 에러 메시지 표시
  function showError(input, msg) {
    let hint = input.nextElementSibling;
    if (!hint || !hint.classList.contains('hint')) {
      hint = document.createElement('small');
      hint.className = 'hint error';
      input.insertAdjacentElement('afterend', hint);
    }
    hint.textContent = msg;
    hint.classList.add('error');
  }

  // 에러 제거
  function clearError(input) {
    let hint = input.nextElementSibling;
    if (hint && hint.classList.contains('hint')) {
      hint.textContent = hint.getAttribute('data-default') || '';
      hint.classList.remove('error');
    }
  }

  // blur 시 개별 필드 검증 + 중복 검사
  async function checkDuplicate(field, value, input) {
    if (!value) return;
    try {
      const res = await fetch(`/users/check-duplicate?field=${field}&value=${encodeURIComponent(value)}`);
      const data = await res.json();
      if (data.exists) {
        showError(input, data.message);
      } else {
        clearError(input);
      }
    } catch (err) {
      console.error("중복 검사 실패", err);
    }
  }

  form.querySelectorAll('input, select').forEach(input => {
    const defaultHint = input.nextElementSibling?.textContent;
    if (defaultHint) input.nextElementSibling.setAttribute('data-default', defaultHint);

    input.addEventListener('blur', e => {
      const value = e.target.value.trim();
      switch (input.name) {
        case 'login_id':
          if (!patterns.login_id.test(value) || value.length < 2) {
            showError(input, 'Login ID는 영문/숫자/특수문자만 가능하며, 최소 2자 이상이어야 합니다.');
          } else {
            clearError(input);
            checkDuplicate('login_id', value, input); // 🔥 중복 검사
          }
          break;
        case 'password':
          if (!patterns.password.test(value) || value.length < 8) {
            showError(input, 'Password는 영문/숫자/특수문자만 가능, 8자 이상이어야 합니다.');
          } else {
            clearError(input);
          }
          break;
        case 'username':
          if (!patterns.username.test(value)) {
            showError(input, '이름은 한글 또는 영문만 가능합니다.');
          } else {
            clearError(input);
          }
          break;
        case 'student_id':
          if (!patterns.student_id.test(value)) {
            showError(input, '학번은 숫자 8자리여야 합니다.');
          } else {
            clearError(input);
            checkDuplicate('student_id', value, input); // 🔥 중복 검사
          }
          break;
        case 'phone':
          if (value && !patterns.phone.test(value)) {
            showError(input, '전화번호 형식이 올바르지 않습니다. 예) 010-1234-5678');
          } else {
            clearError(input);
          }
          break;
      }
    });
  });

  // 전체 메시지 표시
  function showMsg(msg, ok = false) {
    result.textContent = msg;
    result.style.color = ok ? '#0b7a0b' : '#b00020';
  }

  // 최종 유효성 검사 (submit 시 실행)
  function validate() {
    const data = Object.fromEntries(new FormData(form));

    if (!data.login_id || !data.password || !data.username || !data.student_id || !data.major) {
      showMsg('필수 항목을 모두 입력하세요.');
      return false;
    }
    if (!patterns.login_id.test(data.login_id) || data.login_id.length < 2) {
      showMsg('Login ID는 영문/숫자/특수문자만 가능하며, 최소 2자 이상이어야 합니다.');
      return false;
    }
    if (!patterns.password.test(data.password) || data.password.length < 8) {
      showMsg('Password는 영문/숫자/특수문자만 가능, 8자 이상이어야 합니다.');
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

  // submit 이벤트
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    result.textContent = '';

    if (!validate()) return;

    const payload = Object.fromEntries(
      [...new FormData(form)].map(([k, v]) => [k, v.trim()])
    );
    if (!payload.phone) payload.phone = null;

    try {
      const res = await fetch('/users/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        credentials: 'include'
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        if (err.detail) {
          showMsg(err.detail);
        } else if (err.message) {
          showMsg(err.message);
        } else {
          showMsg(`회원가입 실패 (HTTP ${res.status})`);
        }
        return;
      }

      await res.json().catch(() => ({}));
      showMsg('회원가입 신청이 완료되었습니다. 관리자 승인 후 로그인 가능합니다.', true);
      form.reset();
    } catch (err) {
      showMsg(err.message || '네트워크 오류가 발생했습니다.');
    }
  });
})();
