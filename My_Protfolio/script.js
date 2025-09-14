// Typing Animation
const text = ["Aspiring Cloud Engineer", "Frontend Developer", "AI & ML Enthusiast"];
let i = 0, j = 0, currentText = "", isDeleting = false;

function typeEffect() {
  const typingElement = document.querySelector(".typing");

  if (i < text.length) {
    if (!isDeleting && j <= text[i].length) {
      currentText = text[i].substring(0, j++);
    } else if (isDeleting && j >= 0) {
      currentText = text[i].substring(0, j--);
    }

    typingElement.innerHTML = currentText;

    if (j === text[i].length + 1) {
      isDeleting = true;
      setTimeout(typeEffect, 1000);
      return;
    } else if (isDeleting && j === 0) {
      isDeleting = false;
      i++;
      if (i === text.length) i = 0;
    }
  }
  setTimeout(typeEffect, isDeleting ? 50 : 100);
}

typeEffect();
