console.log("midnight lesson trial boot");

window.addEventListener("DOMContentLoaded", () => {
  const button = document.querySelector(".spell-button");
  const title = document.querySelector(".hero-panel h1");
  const sigil = document.querySelector(".sigil-chip");

  if (!button || !title || !sigil) {
    return;
  }

  button.addEventListener("click", () => {
    title.textContent = "Trial Underway";
    sigil.textContent = "Current Test: Lantern Route Active";
    button.textContent = "Focus Held";
  });
});