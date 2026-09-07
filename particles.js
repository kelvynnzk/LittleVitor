(() => {
  const canvas = document.createElement('canvas');
  canvas.className = 'js-teia';
  canvas.setAttribute('aria-hidden', 'true');
  document.body.prepend(canvas);

  const context = canvas.getContext('2d');
  const points = [];
  const connectionDistance = 112;
  let animationId = null;
  let visible = true;

  const style = document.createElement('style');
  style.textContent = `
    .js-teia {
      position: fixed;
      inset: 0;
      z-index: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      opacity: .58;
      mix-blend-mode: screen;
    }
  `;
  document.head.appendChild(style);

  function resize() {
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.floor(window.innerWidth * ratio);
    canvas.height = Math.floor(window.innerHeight * ratio);
    canvas.style.width = `${window.innerWidth}px`;
    canvas.style.height = `${window.innerHeight}px`;
    context.setTransform(ratio, 0, 0, ratio, 0, 0);

    const amount = Math.min(58, Math.max(22, Math.round(window.innerWidth / 25)));
    points.length = 0;
    for (let index = 0; index < amount; index += 1) {
      points.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 0.28,
        vy: (Math.random() - 0.5) * 0.28
      });
    }
  }

  function draw() {
    if (!visible) return;
    context.clearRect(0, 0, window.innerWidth, window.innerHeight);

    points.forEach((point) => {
      point.x += point.vx;
      point.y += point.vy;
      if (point.x < 0 || point.x > window.innerWidth) point.vx *= -1;
      if (point.y < 0 || point.y > window.innerHeight) point.vy *= -1;

      context.fillStyle = 'rgba(255, 255, 255, .8)';
      context.beginPath();
      context.arc(point.x, point.y, 1.35, 0, Math.PI * 2);
      context.fill();
    });

    for (let first = 0; first < points.length; first += 1) {
      for (let second = first + 1; second < points.length; second += 1) {
        const distance = Math.hypot(
          points[first].x - points[second].x,
          points[first].y - points[second].y
        );
        if (distance < connectionDistance) {
          context.strokeStyle = `rgba(167, 139, 250, ${0.18 * (1 - distance / connectionDistance)})`;
          context.lineWidth = 1;
          context.beginPath();
          context.moveTo(points[first].x, points[first].y);
          context.lineTo(points[second].x, points[second].y);
          context.stroke();
        }
      }
    }

    animationId = requestAnimationFrame(draw);
  }

  const observer = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    if (visible && animationId === null) draw();
    if (!visible && animationId !== null) {
      cancelAnimationFrame(animationId);
      animationId = null;
    }
  });

  resize();
  observer.observe(canvas);
  window.addEventListener('resize', resize, { passive: true });
  draw();
})();
