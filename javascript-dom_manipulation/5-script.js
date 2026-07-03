const updateHeader = document.querySelector("#update_header");
const header = document.querySelector("header");

updateHeader.addEventListener("click", () => {
  header.textContent = "New Header!!!";
});
