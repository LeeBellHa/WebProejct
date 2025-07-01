const floorRooms = {
  '1F': ['125호', '126호', '127-2호', '127-3호', '127-4호', '127-5호', '129호'],
  '2F': [...Array(13).keys()].map(i => `222-${i+2}호`).concat(['225호','226호','227호','228호','229호','230호']),
  '3F': ['325호', '326호', '327호', '328호', '329호', '330호', '331호'],
  '4F': [...Array(6).keys()].map(i => `419-0${i+1}호`).concat([...Array(6).keys()].map(i => `420-0${i+1}호`))
};

const days = [...Array(7).keys()].map(i => {
  const d = new Date();
  d.setDate(d.getDate() + i);
  return d;
});

document.getElementById("dateButtons").innerHTML = days.map(d => {
  const label = `${d.getMonth()+1}월 ${d.getDate()}일 (${d.toLocaleDateString('ko-KR', { weekday: 'short' })})`;
  return `<button onclick="selectDate('${label}')">${label}</button>`;
}).join('');

let selectedDate = "";
let selectedFloor = "";
let selectedRoom = "";

function selectDate(date) {
  selectedDate = date;
  checkReady();
}

function selectFloor(floor) {
  selectedFloor = floor;
  const rooms = floorRooms[floor];
  document.getElementById("roomButtons").innerHTML = rooms.map(room => `<button onclick="selectRoom('${room}')">${room}</button>`).join('');
}

function selectRoom(room) {
  selectedRoom = room;
  checkReady();
}

function checkReady() {
  if (selectedDate && selectedRoom && selectedFloor) {
    showPopup();
  }
}

let selectedTime = "";

function showPopup() {
  const popup = document.createElement("div");
  popup.className = "popup";
  popup.innerHTML = `
    <div class="popup-inner">
      <button class="close-btn" onclick="this.closest('.popup').remove()">✖</button>
      <h3>${selectedDate} ${selectedFloor} ${selectedRoom} 시간 선택</h3>
      <div class="time-slot" id="timeSlot">
        ${Array.from({length: 15}, (_, i) => i + 9).map(h => `<button onclick="selectTime(this, '${String(h).padStart(2,'0')}:00')">${String(h).padStart(2,'0')}:00</button>`).join('')}
      </div>
      <button id="reserveBtn" style="margin-top: 1rem; padding: 0.7rem; width: 100%; background-color: #0026b3; color: white; border: none; border-radius: 6px; cursor: pointer;" onclick="submitReservation()">예약하기</button>
    </div>
  `;
  document.getElementById("popupContainer").appendChild(popup);
}

function selectTime(button, time) {
  selectedTime = time;
  const all = document.querySelectorAll(".time-slot button");
  all.forEach(b => b.style.backgroundColor = "#d9e1f2");
  button.style.backgroundColor = "#7aa4f7";
}

function submitReservation() {
  if (!selectedTime) {
    alert("시간을 선택해주세요.");
    return;
  }
  alert(`예약 완료: ${selectedDate} ${selectedRoom} ${selectedTime}`);
  document.querySelector(".popup")?.remove();
}
  const popup = document.createElement("div");
  popup.className = "popup";
  popup.innerHTML = `
    <div class="popup-inner">
      <button class="close-btn" onclick="this.closest('.popup').remove()">✖</button>
      <h3>${selectedDate} ${selectedFloor} ${selectedRoom} 시간 선택</h3>
      <div class="time-slot">
        ${Array.from({length: 15}, (_, i) => i + 9).map(h => `<button>${String(h).padStart(2,'0')}:00</button>`).join('')}
      </div>
    </div>
  `;
  document.getElementById("popupContainer").appendChild(popup);

