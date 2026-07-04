function openLoginModal() {
    document.getElementById("loginModal").style.display = "flex";
}

function closeLoginModal() {
    document.getElementById("loginModal").style.display = "none";
}

window.onclick = function(event) {
    const modal = document.getElementById("loginModal");

    if (event.target === modal) {
        modal.style.display = "none";
    }
};

/* -----------------------------------
   Floating Tech Icons
   Left and Right Side Falling Effect
----------------------------------- */

const skills = [
    // Python Full Stack
    { icon: "devicon-python-plain", name: "Python" },
    { icon: "devicon-django-plain", name: "Django" },
    { icon: "devicon-html5-plain", name: "HTML5" },
    { icon: "devicon-css3-plain", name: "CSS3" },
    { icon: "devicon-javascript-plain", name: "JavaScript" },
    { icon: "devicon-bootstrap-plain", name: "Bootstrap" },
    { icon: "devicon-mysql-plain", name: "MySQL" },

    // Data Analysis Tools
    { icon: "devicon-python-plain", name: "Pandas" },
    { icon: "devicon-numpy-plain", name: "NumPy" },
    { icon: "fas fa-chart-line", name: "Power BI" },
    { icon: "fas fa-file-excel", name: "Excel" },
    { icon: "fas fa-database", name: "SQL" },
    { icon: "fas fa-chart-bar", name: "Tableau" },

    // Java Full Stack
    { icon: "devicon-java-plain", name: "Java" },
    { icon: "devicon-spring-plain", name: "Spring" },
    { icon: "devicon-angularjs-plain", name: "Angular" },
    { icon: "devicon-react-original", name: "React" },
    { icon: "devicon-oracle-original", name: "Oracle" },

    // Embedded Tools
    { icon: "devicon-c-plain", name: "C" },
    { icon: "devicon-cplusplus-plain", name: "C++" },
    { icon: "devicon-arduino-plain", name: "Arduino" },
    { icon: "fas fa-microchip", name: "Embedded C" },
    { icon: "fas fa-memory", name: "Microcontroller" },
    { icon: "fas fa-tools", name: "Proteus" }
];

function createFloatingIcons() {
    const container = document.getElementById("floatingIcons");

    if (!container) return;

    container.innerHTML = "";

    const count = window.innerWidth <= 768 ? 20 : 38;

    for (let i = 0; i < count; i++) {
        const skill = skills[Math.floor(Math.random() * skills.length)];
        const div = document.createElement("div");

        div.className = "skill-icon";

        let leftPosition;

        /*
            Left side: 1% to 17%
            Right side: 82% to 96%
            Center hero section is avoided.
        */
        if (i % 2 === 0) {
            leftPosition = 1 + Math.random() * 16;
        } else {
            leftPosition = 82 + Math.random() * 14;
        }

        const startTop = -180 - Math.random() * 300;
        const duration = 9 + Math.random() * 9;
        const delay = Math.random() * 12;
        const scale = 0.75 + Math.random() * 0.45;
        const opacity = 0.72 + Math.random() * 0.28;

        div.style.left = `${leftPosition}%`;
        div.style.top = `${startTop}px`;
        div.style.animationDuration = `${duration}s`;
        div.style.animationDelay = `${delay}s`;
        div.style.opacity = opacity;
        div.style.scale = scale;

        div.innerHTML = `<i class="${skill.icon}"></i><span>${skill.name}</span>`;

        container.appendChild(div);
    }
}

createFloatingIcons();

window.addEventListener("resize", function() {
    createFloatingIcons();
});

/* -----------------------------------
   Neural Network Background Animation
----------------------------------- */

const canvas = document.getElementById("networkCanvas");
const ctx = canvas.getContext("2d");

let particles = [];
const particleCount = 75;

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

resizeCanvas();
window.addEventListener("resize", resizeCanvas);

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.vx = (Math.random() - 0.5) * 0.7;
        this.vy = (Math.random() - 0.5) * 0.7;
        this.radius = Math.random() * 2.2 + 1.2;
    }

    move() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x <= 0 || this.x >= canvas.width) {
            this.vx *= -1;
        }

        if (this.y <= 0 || this.y >= canvas.height) {
            this.vy *= -1;
        }
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(255, 110, 110, 0.8)";
        ctx.fill();
    }
}

function initParticles() {
    particles = [];

    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
}

initParticles();

function connectParticles() {
    for (let a = 0; a < particles.length; a++) {
        for (let b = a + 1; b < particles.length; b++) {
            const dx = particles[a].x - particles[b].x;
            const dy = particles[a].y - particles[b].y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 130) {
                ctx.beginPath();
                ctx.moveTo(particles[a].x, particles[a].y);
                ctx.lineTo(particles[b].x, particles[b].y);
                ctx.strokeStyle = `rgba(255, 80, 80, ${1 - distance / 130})`;
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        }
    }
}

function animateNetwork() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let particle of particles) {
        particle.move();
        particle.draw();
    }

    connectParticles();
    requestAnimationFrame(animateNetwork);
}

animateNetwork();