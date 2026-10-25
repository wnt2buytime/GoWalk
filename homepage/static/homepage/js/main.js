// Небольшое клиентское поведение интерфейса GoWalk.

// Текущий год в подвале страницы.
const yearElement = document.getElementById("current-year");
if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
}

// Быстрый отбор карточек маршрутов по сложности без перезагрузки страницы.
const filterButtons = document.querySelectorAll("[data-difficulty-filter]");
const routeCards = document.querySelectorAll("[data-difficulty]");
const visibleCounter = document.getElementById("visible-routes");

filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const difficulty = button.dataset.difficultyFilter;
        let visible = 0;
        routeCards.forEach((card) => {
            const show = difficulty === "all" || card.dataset.difficulty === difficulty;
            card.classList.toggle("d-none", !show);
            if (show) {
                visible += 1;
            }
        });
        filterButtons.forEach((other) => other.classList.remove("active"));
        button.classList.add("active");
        if (visibleCounter) {
            visibleCounter.textContent = visible;
        }
    });
});
