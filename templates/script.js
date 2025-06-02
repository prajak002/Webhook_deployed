async function fetchEvents() {
  const res = await fetch('/events');
  const data = await res.json();
  const container = document.getElementById('events');
  container.innerHTML = "";
  data.forEach(e => {
    const ts = new Date(e.timestamp).toUTCString();
    if (e.type === "PUSH") {
      container.innerHTML += `<p>${e.author} pushed to ${e.to_branch} on ${ts}</p>`;
    } else if (e.type === "PULL_REQUEST") {
      container.innerHTML += `<p>${e.author} submitted a pull request from ${e.from_branch} to ${e.to_branch} on ${ts}</p>`;
    } else if (e.type === "MERGE") {
      container.innerHTML += `<p>${e.author} merged branch ${e.from_branch} to ${e.to_branch} on ${ts}</p>`;
    }
  });
}

fetchEvents();
setInterval(fetchEvents, 15000);
