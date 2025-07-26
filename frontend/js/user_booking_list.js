document.addEventListener("DOMContentLoaded", () => {
  // 로그인에서 저장한 키 이름에 맞춰서 가져오기
  const token = localStorage.getItem("token"); // 🔑 여기!
  if (!token) {
    alert("로그인이 필요합니다.");
    location.href = "index.html";
    return;
  }

  const headers = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  };

  fetch("/api/bookings/me", { headers })
    .then(res => {
      if (!res.ok) throw new Error("예약 내역 불러오기 실패");
      return res.json();
    })
    .then(bookings => {
      const tbody = document.querySelector("#bookingTable tbody");
      tbody.innerHTML = "";
      if (bookings.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4">예약 내역이 없습니다.</td></tr>`;
        return;
      }
      bookings.forEach(b => {
        const startTime = b.start_time.substring(0, 5);
        const endTime = b.end_time.substring(0, 5);
        const [sh, sm] = startTime.split(":").map(Number);
        const [eh, em] = endTime.split(":").map(Number);
        const diffHours = ((eh * 60 + em) - (sh * 60 + sm)) / 60;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${b.start_date}</td>
          <td>${startTime}</td>
          <td>${endTime}</td>
          <td>${diffHours}시간</td>
        `;
        tbody.appendChild(tr);
      });
    })
    .catch(err => {
      console.error(err);
      alert("예약 내역을 불러올 수 없습니다.");
    });
});
