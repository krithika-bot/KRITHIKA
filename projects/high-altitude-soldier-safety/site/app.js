(() => {
  const heroScene = document.querySelector('#heroScene');
  const spinToggle = document.querySelector('#spinToggle');
  let spinning = true;

  spinToggle?.addEventListener('click', () => {
    spinning = !spinning;
    heroScene?.classList.toggle('paused', !spinning);
    spinToggle.setAttribute('aria-pressed', String(spinning));
    spinToggle.setAttribute('aria-label', spinning ? 'Pause 3D rotation' : 'Resume 3D rotation');
    spinToggle.textContent = spinning ? 'Ⅱ' : '▶';
  });

  const stage = document.querySelector('#explodeStage');
  const viewButtons = [...document.querySelectorAll('.view-btn')];
  viewButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const view = button.dataset.view;
      stage.dataset.view = view;
      viewButtons.forEach((item) => {
        const active = item === button;
        item.classList.toggle('active', active);
        item.setAttribute('aria-pressed', String(active));
      });
    });
  });

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduceMotion && heroScene) heroScene.classList.add('paused');
})();
