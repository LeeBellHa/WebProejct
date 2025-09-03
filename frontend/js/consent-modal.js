(function () {
  const modal = document.getElementById('consentModal');
  const openBtn = document.getElementById('openConsent');
  const agreeBtn = document.getElementById('agreeBtn');
  const consentCheckbox = document.getElementById('consentRequired');

  function openModal() {
    modal.classList.add('show');
    modal.setAttribute('aria-hidden', 'false');
    // 포커스 이동(접근성)
    setTimeout(() => modal.querySelector('.modal-close').focus(), 0);
    document.body.style.overflow = 'hidden';
  }
  function closeModal() {
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  openBtn?.addEventListener('click', openModal);
  modal.querySelectorAll('[data-close]').forEach(el => {
    el.addEventListener('click', closeModal);
  });
  agreeBtn?.addEventListener('click', () => {
    consentCheckbox.checked = true;
    closeModal();
  });

  // ESC 닫기
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('show')) closeModal();
  });
})();
