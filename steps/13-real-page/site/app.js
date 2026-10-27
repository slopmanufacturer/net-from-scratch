async function load() {
  const response = await fetch("/api/time");
  const data = await response.json();
  document.getElementById("time").textContent = data.time;
}

document.getElementById("refresh").addEventListener("click", load);
load();
