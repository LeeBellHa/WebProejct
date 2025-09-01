document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("로그인이 필요합니다.");
    location.href = "index.html";
    return;
  }

  const headers = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  };

  // 🔑 로그아웃 이벤트 추가
  const logoutBtn = document.getElementById("logout");
  if (logoutBtn) {
    logoutBtn.onclick = () => {
      localStorage.removeItem("token");
      location.href = "index.html";
    };
  }

  // KST 현재 시간
  function nowInKST() {
    return new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Seoul" }));
  }

  fetch("/api/bookings/me", { headers })
    .then(res => {
      if (!res.ok) throw new Error("예약 내역 불러오기 실패");
      return res.json();
    })
    .then(bookings => {
      const tbody = document.querySelector("#bookingTable tbody");
      tbody.innerHTML = "";
      if (bookings.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5">예약 내역이 없습니다.</td></tr>`;
        return;
      }

      bookings.forEach(b => {
        const startTime = b.start_time.substring(0, 5);
        const endTime = b.end_time.substring(0, 5);
        const [sh, sm] = startTime.split(":").map(Number);
        const [eh, em] = endTime.split(":").map(Number);
        const diffHours = ((eh * 60 + em) - (sh * 60 + sm)) / 60;

        // 예약 시작 datetime (KST)
        const startDt = new Date(`${b.start_date}T${b.start_time}+09:00`);
        const now = nowInKST();
        const diffSec = (startDt - now) / 1000;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${b.start_date}</td>
          <td>${startTime}</td>
          <td>${endTime}</td>
          <td>${diffHours}시간</td>
          <td class="cancel-cell"></td>
        `;

        if (diffSec > 600) {
          const btn = document.createElement("button");
          btn.textContent = "취소";
          btn.className = "btn-cancel";
          btn.onclick = async () => {
            if (!confirm("정말 예약을 취소하시겠습니까?")) return;
            try {
              const res = await fetch(`/api/bookings/${b.booking_id}`, {
                method: "DELETE",
                headers
              });
              if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                alert(err.detail || "취소 실패");
                return;
              }
              alert("예약이 취소되었습니다.");
              tr.remove();
            } catch (err) {
              console.error(err);
              alert("취소 실패");
            }
          };
          tr.querySelector(".cancel-cell").appendChild(btn);
        }

        tbody.appendChild(tr);
      });
    })
    .catch(err => {
      console.error(err);
      alert("예약 내역을 불러올 수 없습니다.");
    });
});
