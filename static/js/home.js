document.addEventListener('DOMContentLoaded', () => {
    // === 3D CARD CAROUSEL LOGIC ===
    const cards = document.querySelectorAll('.c-card');
    const wrapper = document.querySelector('.carousel-3d-wrapper');

    let currentIndex = 0;
    const totalCards = cards.length;
    let slideInterval;

    function updateCards() {
        if (totalCards === 0) return;
        cards.forEach((card, index) => {
            // Reset classes
            card.classList.remove('active', 'prev', 'next', 'hidden');

            // Determine position relative to current index
            // We need to handle circular logic carefully

            // Calculate "distance" from current index, handling wrap-around
            let diff = (index - currentIndex + totalCards) % totalCards;
            // diff = 0 -> Active
            // diff = 1 -> Next
            // diff = totalCards - 1 -> Prev

            if (diff === 0) {
                card.classList.add('active');
            } else if (diff === 1 && totalCards > 1) {
                card.classList.add('next');
            } else if (diff === totalCards - 1 && totalCards > 1) {
                card.classList.add('prev');
            } else {
                card.classList.add('hidden');
            }
        });
    }

    function nextSlide() {
        if (totalCards <= 1) return;
        currentIndex = (currentIndex + 1) % totalCards;
        updateCards();
    }

    function prevSlide() {
        if (totalCards <= 1) return;
        currentIndex = (currentIndex - 1 + totalCards) % totalCards;
        updateCards();
    }

    // Initialize
    updateCards();

    // GLOBAL FUNCTION FOR ONCLICK (Exposed to window)
    window.moveCarousel = function (direction) {
        if (direction === 1) {
            nextSlide();
        } else {
            prevSlide();
        }
        resetTimer();
    };

    // Click on side cards to navigate
    cards.forEach((card, index) => {
        card.addEventListener('click', () => {
            if (card.classList.contains('next')) {
                nextSlide();
                resetTimer();
            } else if (card.classList.contains('prev')) {
                prevSlide();
                resetTimer();
            }
        });
    });

    // Auto slide
    function startTimer() {
        if (totalCards > 1) {
            slideInterval = setInterval(nextSlide, 3500); // 3.5 seconds
        }
    }

    function stopTimer() {
        clearInterval(slideInterval);
    }

    function resetTimer() {
        stopTimer();
        startTimer();
    }

    // Pause on hover
    if (wrapper) {
        wrapper.addEventListener('mouseenter', stopTimer);
        wrapper.addEventListener('mouseleave', startTimer);
    }

    // Start initially
    startTimer();

    // === COUNTER ANIMATION ===
    const statNumbers = document.querySelectorAll('.stat-number');

    const counterObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const endValue = parseInt(target.getAttribute('data-target'));
                const duration = 2000; // 2 seconds
                const startTime = performance.now();

                function updateCounter(currentTime) {
                    const elapsed = currentTime - startTime;
                    const progress = Math.min(elapsed / duration, 1);

                    // Easing function (easeOutExpo)
                    const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);

                    const currentValue = Math.floor(endValue * ease);
                    target.innerText = currentValue;

                    if (progress < 1) {
                        requestAnimationFrame(updateCounter);
                    } else {
                        target.innerText = endValue; // Ensure exact final value
                    }
                }

                requestAnimationFrame(updateCounter);
                observer.unobserve(target); // Only animate once
            }
        });
    }, { threshold: 0.5 });

    statNumbers.forEach(stat => counterObserver.observe(stat));


    // === AUTO-MOVING CAROUSEL LOGIC ===
    function initCarousel(wrapperId, trackId) {
        const wrapper = document.getElementById(wrapperId);
        const track = document.getElementById(trackId);

        if (!wrapper || !track) return;

        const cards = [...track.querySelectorAll('.carousel-card')];
        if (cards.length === 0) return;

        // Duplicate cards for infinite loop
        cards.forEach(card => {
            const clone = card.cloneNode(true);
            track.appendChild(clone);
        });

        const cardWidth = cards[0].offsetWidth + 30; // card width + gap
        const totalWidth = cardWidth * cards.length;
        let currentX = 0;
        let isPaused = false;
        let rafId = null;

        function animate() {
            if (!isPaused) {
                currentX -= 0.8; // Speed of auto-scroll
                if (Math.abs(currentX) >= totalWidth) {
                    currentX = 0;
                }
                track.style.transform = `translateX(${currentX}px)`;
            }
            rafId = requestAnimationFrame(animate);
        }

        // Start animation
        animate();

        // Pause on hover
        wrapper.addEventListener('mouseenter', () => isPaused = true);
        wrapper.addEventListener('mouseleave', () => isPaused = false);

        // Arrow navigation
        const prevBtn = wrapper.querySelector('.carousel-prev');
        const nextBtn = wrapper.querySelector('.carousel-next');

        if (prevBtn && nextBtn) {
            let isMoving = false;

            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (isMoving) return;
                isMoving = true;
                isPaused = true;

                // Calculate nearest alignment
                const targetX = Math.round((currentX - cardWidth) / cardWidth) * cardWidth;

                track.style.transition = 'transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                currentX = targetX;

                // Handle wrap-around
                if (Math.abs(currentX) >= totalWidth) {
                    currentX = 0;
                    track.style.transform = `translateX(${currentX}px)`;
                } else {
                    track.style.transform = `translateX(${currentX}px)`;
                }

                setTimeout(() => {
                    track.style.transition = 'none';
                    isMoving = false;
                    isPaused = false;
                }, 500);
            });

            prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (isMoving) return;
                isMoving = true;
                isPaused = true;

                // Calculate nearest alignment
                let targetX = Math.round((currentX + cardWidth) / cardWidth) * cardWidth;

                track.style.transition = 'transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';

                if (targetX > 0) {
                    // Secret jump to end for seamless back-scroll
                    track.style.transition = 'none';
                    currentX = -totalWidth;
                    track.style.transform = `translateX(${currentX}px)`;
                    targetX = currentX + cardWidth;

                    requestAnimationFrame(() => {
                        track.style.transition = 'transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                        currentX = targetX;
                        track.style.transform = `translateX(${currentX}px)`;
                    });
                } else {
                    currentX = targetX;
                    track.style.transform = `translateX(${currentX}px)`;
                }

                setTimeout(() => {
                    track.style.transition = 'none';
                    isMoving = false;
                    isPaused = false;
                }, 500);
            });
        }
    }

    // Initialize carousels
    initCarousel('notice-carousel', 'notice-track');
    initCarousel('rt-carousel', 'rt-track');
});
