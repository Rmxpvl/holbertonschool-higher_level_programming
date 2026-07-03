const redheader = document.querySelector("#red_header");
const header = document.querySelector("header");

redheader.addEventListener("click", () => {
  header.classList.add("red");
});
