async function loadData() {
  try {
    const res = await fetch("analytics.json");
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

    const data = await res.json();
    const record = data[0];

    document.getElementById('count-users').innerText = record.count_users.toLocaleString();
    document.getElementById('count-users-today').innerText = record.count_users_today.toLocaleString();
    document.getElementById('count-messages').innerText = record.count_messages.toLocaleString();
    document.getElementById('count-messages-today').innerText = record.count_messages_today.toLocaleString();

    function fillHoursData(hours, counts) {
      const filledCounts = Array(24).fill(0);
      hours.forEach((hour, index) => {
        if (hour >= 0 && hour < 24) {
          const timezoneOffset = new Date().getTimezoneOffset() / 60;
          const adjustedHour = (hour - timezoneOffset) % 24;
          filledCounts[adjustedHour] = counts[index];
        }
      });
      return filledCounts;
    }

    const labels = Array.from({ length: 24 }, (_, i) => i);
    const counts = fillHoursData(record.count_messages_per_hour.hours, record.count_messages_per_hour.count_messages);

    const ctx = document.getElementById('messages-hour-chart').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Сообщения по часам',
          data: counts,
          backgroundColor: 'rgba(0, 115, 230, 0.7)',
          borderColor: 'rgba(0, 115, 230, 1)',
          borderWidth: 1,
          borderRadius: 4,
        }]
      },
      options: {
        scales: {
          y: { beginAtZero: true, ticks: { precision: 0 }, title: { display: true, text: 'Сообщения'} },
          x: { title: { display: true, text: 'Часы' } }
        },
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => `${ctx.parsed.y} сообщений` } }
        }
      }
    });

  } catch (e) {
    document.getElementById("dashboard").innerText = "Ошибка загрузки данных: " + e.message;
    console.error(e);
  }
}

loadData();
