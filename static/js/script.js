document.addEventListener('DOMContentLoaded', function () {
  const cards = document.querySelectorAll('.card');
  
  cards.forEach(card => {
    const input = card.querySelector('input[type="radio"]');
    card.addEventListener('click', () => {
      if (!input.disabled) {
        input.checked = true;
        cards.forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
      }
    });

    input.addEventListener('change', () => {
      cards.forEach(c => c.classList.remove('selected'));
      if (input.checked) {
        card.classList.add('selected');
      }
    });
  });
});
