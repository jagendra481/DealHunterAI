/* =====================================================
   DEALHUNTERAI - 3D INTERACTIVE TILT & PARALLAX ENGINE
===================================================== */

document.addEventListener("DOMContentLoaded", () => {
    init3DAssembly();
    init3DTiltEffects();
    initSearchBox();
});

// 3D "Assemble into Place" Staggered Fly-In Entrance Effect
function init3DAssembly() {
    const elements = document.querySelectorAll(".card, .profile-stat-card, .btn-lg, .table-responsive, .nav-pills");

    elements.forEach((el, index) => {
        const colIndex = index % 3;
        let offsetX = 0;
        if (colIndex === 0) offsetX = -70;
        else if (colIndex === 2) offsetX = 70;

        const offsetY = 60 + (index * 8);
        const offsetZ = -180;
        const rotateX = 15;
        const rotateY = colIndex === 0 ? -12 : (colIndex === 2 ? 12 : 0);

        el.style.opacity = "0";
        el.style.transformStyle = "preserve-3d";
        el.style.transform = `perspective(1200px) translate3d(${offsetX}px, ${offsetY}px, ${offsetZ}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(0.75)`;
        el.style.transition = "none";

        setTimeout(() => {
            el.style.transition = "transform 0.85s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.75s ease-out";
            el.style.opacity = "1";
            el.style.transform = "perspective(1000px) translate3d(0, 0, 0) rotateX(0deg) rotateY(0deg) scale(1)";
        }, 80 + (index * 60));
    });
}

function init3DTiltEffects() {
    const tiltTargets = document.querySelectorAll(".card, .profile-stat-card, .tilt-3d");

    tiltTargets.forEach(card => {
        card.style.transformStyle = "preserve-3d";
        card.style.perspective = "1000px";

        let glare = card.querySelector(".glare-3d");
        if (!glare) {
            glare = document.createElement("div");
            glare.className = "glare-3d";
            glare.style.cssText = `
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                border-radius: inherit;
                pointer-events: none;
                background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0) 70%);
                opacity: 0;
                transition: opacity 0.3s ease;
                z-index: 10;
            `;
            card.style.position = "relative";
            card.style.overflow = "hidden";
            card.appendChild(glare);
        }

        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = ((y - centerY) / centerY) * -12;
            const rotateY = ((x - centerX) / centerX) * 12;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px) scale3d(1.02, 1.02, 1.02)`;
            card.style.transition = "transform 0.1s cubic-bezier(0.03, 0.98, 0.52, 0.99)";

            const glareX = (x / rect.width) * 100;
            const glareY = (y / rect.height) * 100;
            glare.style.background = `radial-gradient(circle at ${glareX}% ${glareY}%, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 65%)`;
            glare.style.opacity = "1";
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px) scale3d(1, 1, 1)";
            card.style.transition = "transform 0.5s cubic-bezier(0.25, 1, 0.5, 1)";
            if (glare) {
                glare.style.opacity = "0";
            }
        });
    });
}

function initSearchBox() {
    const searchBox = document.getElementById("searchBox");
    const suggestions = document.getElementById("suggestions");

    if (searchBox && suggestions) {
        searchBox.addEventListener("keyup", async () => {
            const q = searchBox.value.trim();
            if (q.length < 2) {
                suggestions.innerHTML = "";
                return;
            }

            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
                const products = await response.json();
                suggestions.innerHTML = "";

                products.forEach(product => {
                    suggestions.innerHTML += `
                        <a href="/products" class="list-group-item list-group-item-action border-0 py-2 shadow-sm rounded-3 mb-1">
                            <i class="bi bi-search me-2 text-primary"></i> ${product.name}
                        </a>
                    `;
                });
            } catch (err) {
                console.error("Search error:", err);
            }
        });
    }
}
