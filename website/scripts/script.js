const badge = document.getElementById('badge');
const hint = document.getElementById('rotate-hint');
const portrait = window.matchMedia('(orientation: portrait)');

// Scale the badge to 90% of the width, and also at most 90% of the height in landscape
function fit() {
  badge.style.transform = 'none';
  const w = badge.offsetWidth;
  const h = badge.offsetHeight;
  if (!w || !h) return;

  let scale = (window.innerWidth * 0.9) / w;
  if (!portrait.matches) {
    scale = Math.min(scale, (window.innerHeight * 0.9) / h);
  }
  badge.style.transform = 'scale(' + scale + ')';
}

// The badge loads asynchronously, so re-fit whenever its size changes
new ResizeObserver(fit).observe(badge);
window.addEventListener('resize', fit);
window.addEventListener('load', fit);
portrait.addEventListener('change', fit);

// Browsers don't allow forcing landscape, except via fullscreen on Android.
// Tapping the hint tries that; if it's unsupported, the animation still guides the user.
hint.addEventListener('click', async () => {
  try {
    await document.documentElement.requestFullscreen();
    await screen.orientation.lock('landscape');
  } catch (e) {
    /* not supported (e.g. iOS), ignore */
  }
});
