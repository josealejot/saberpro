/**
 * SIMULADOR SABER 5° - Lógica Interactiva en Cliente
 * Desarrollado para Isaías Tangarife
 */

document.addEventListener('DOMContentLoaded', () => {
  initSimulador();
});

function initSimulador() {
  const formSimulador = document.getElementById('form-simulador');
  if (!formSimulador) return;

  const questionCards = document.querySelectorAll('.question-card');
  const totalQuestions = questionCards.length;
  if (totalQuestions === 0) return;

  let currentIndex = 0;
  let elapsedSeconds = 0;

  // Elementos UI
  const timerText = document.getElementById('timer-text');
  const inputTiempo = document.getElementById('input-tiempo-segundos');
  const progressBarFill = document.getElementById('progress-bar-fill');
  const progressIndicator = document.getElementById('progress-question-indicator');
  const progressPercent = document.getElementById('progress-percent');
  const countAnsweredEl = document.getElementById('count-answered');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  const btnFinish = document.getElementById('btn-finish');
  const questionPills = document.querySelectorAll('.question-pill');

  // Modal
  const modalConfirm = document.getElementById('modal-confirm');
  const modalMsg = document.getElementById('modal-msg');
  const btnModalCancel = document.getElementById('btn-modal-cancel');
  const btnModalConfirm = document.getElementById('btn-modal-confirm');

  // 1. Cronómetro de Aventura
  const timerInterval = setInterval(() => {
    elapsedSeconds++;
    if (inputTiempo) inputTiempo.value = elapsedSeconds;

    const mins = Math.floor(elapsedSeconds / 60);
    const secs = elapsedSeconds % 60;
    if (timerText) {
      timerText.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
  }, 1000);

  // 2. Control de Preguntas y Navegación
  function showQuestion(index) {
    if (index < 0 || index >= totalQuestions) return;

    questionCards.forEach((card, idx) => {
      if (idx === index) {
        card.classList.remove('hidden-question');
        card.classList.add('current-question');
      } else {
        card.classList.remove('current-question');
        card.classList.add('hidden-question');
      }
    });

    questionPills.forEach((pill, idx) => {
      if (idx === index) {
        pill.classList.add('active');
        pill.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      } else {
        pill.classList.remove('active');
      }
    });

    currentIndex = index;

    // Actualizar botones
    btnPrev.disabled = (currentIndex === 0);

    if (currentIndex === totalQuestions - 1) {
      btnNext.classList.add('hidden-btn');
      btnFinish.classList.remove('hidden-btn');
    } else {
      btnNext.classList.remove('hidden-btn');
      btnFinish.classList.add('hidden-btn');
    }

    updateProgress();
  }

  // 3. Seguimiento de Respuestas y Progreso
  function updateProgress() {
    let answeredCount = 0;

    questionCards.forEach((card) => {
      const qid = card.getAttribute('data-qid');
      const isAnswered = card.querySelector(`input[name="preg_${qid}"]:checked`);
      const pill = document.getElementById(`pill-${qid}`);

      if (isAnswered) {
        answeredCount++;
        if (pill) pill.classList.add('answered');
      } else {
        if (pill) pill.classList.remove('answered');
      }
    });

    if (countAnsweredEl) countAnsweredEl.textContent = answeredCount;

    // Porcentaje de avance
    const pct = Math.round((answeredCount / totalQuestions) * 100);
    if (progressBarFill) progressBarFill.style.width = `${pct}%`;
    if (progressPercent) progressPercent.textContent = `${pct}% completado`;
    if (progressIndicator) {
      progressIndicator.textContent = `Pregunta ${currentIndex + 1} de ${totalQuestions}`;
    }
  }

  // Eventos de selección de radio
  const radioInputs = document.querySelectorAll('.option-radio');
  radioInputs.forEach(radio => {
    radio.addEventListener('change', () => {
      updateProgress();
    });
  });

  // Eventos de botones
  btnPrev.addEventListener('click', () => {
    if (currentIndex > 0) showQuestion(currentIndex - 1);
  });

  btnNext.addEventListener('click', () => {
    if (currentIndex < totalQuestions - 1) showQuestion(currentIndex + 1);
  });

  questionPills.forEach((pill, idx) => {
    pill.addEventListener('click', () => {
      showQuestion(idx);
    });
  });

  // 4. Modal de Confirmación Amigable
  btnFinish.addEventListener('click', () => {
    const answeredCount = parseInt(countAnsweredEl.textContent, 10) || 0;
    const missing = totalQuestions - answeredCount;

    if (missing > 0) {
      modalMsg.innerHTML = `Isaías, tienes <strong>${missing} ${missing === 1 ? 'pregunta' : 'preguntas'} sin responder</strong>.<br>¿Deseas revisarlas o prefieres entregar la prueba así?`;
      btnModalConfirm.textContent = 'Entregar de todas formas 🚀';
    } else {
      modalMsg.innerHTML = `¡Fantástico, Isaías! Respondiste las <strong>${totalQuestions} preguntas</strong>.<br>¿Listo para calcular tu puntaje oficial ICFES?`;
      btnModalConfirm.textContent = '¡Sí, calcular mi puntaje! 🏆';
    }

    modalConfirm.classList.remove('hidden-modal');
  });

  btnModalCancel.addEventListener('click', () => {
    modalConfirm.classList.add('hidden-modal');
  });

  btnModalConfirm.addEventListener('click', () => {
    clearInterval(timerInterval);
    formSimulador.submit();
  });

  // Iniciar en la primera pregunta
  showQuestion(0);
}

// ====================================================================
// EFECTO CONFETI PARA CELEBRAR EL REPORTE DE ISAÍAS
// ====================================================================
function dispararConfetti() {
  const canvas = document.getElementById('confetti-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const colors = ['#38bdf8', '#22c55e', '#facc15', '#f97316', '#a855f7', '#ec4899'];
  const confettiCount = 120;
  const particles = [];

  for (let i = 0; i < confettiCount; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height - height,
      size: Math.random() * 10 + 6,
      color: colors[Math.floor(Math.random() * colors.length)],
      speedY: Math.random() * 3 + 2,
      speedX: Math.random() * 4 - 2,
      rotation: Math.random() * 360,
      rotationSpeed: Math.random() * 10 - 5
    });
  }

  let animationFrame;
  let framesCount = 0;

  function render() {
    ctx.clearRect(0, 0, width, height);

    particles.forEach(p => {
      p.y += p.speedY;
      p.x += p.speedX;
      p.rotation += p.rotationSpeed;

      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate((p.rotation * Math.PI) / 180);
      ctx.fillStyle = p.color;
      ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
      ctx.restore();

      if (p.y > height) {
        p.y = -10;
        p.x = Math.random() * width;
      }
    });

    framesCount++;
    if (framesCount < 300) { // Cae confeti durante ~5 segundos
      animationFrame = requestAnimationFrame(render);
    } else {
      ctx.clearRect(0, 0, width, height);
    }
  }

  render();
}
