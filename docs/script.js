// Configuración global
const CONFIG = {
    githubUser: 'NightWalkAX',
    repoName: 'floating_cheatsheets',
    version: null
};

// Cargar versión dinámicamente
async function loadVersion() {
    try {
        const response = await fetch('./version.json');
        const data = await response.json();
        CONFIG.version = data.version;
        updateVersionElements();
    } catch (error) {
        console.warn('No se pudo cargar la versión dinámicamente, usando versión por defecto');
        CONFIG.version = '1.0.0';
        updateVersionElements();
    }
}

// Actualizar todos los elementos que contienen la versión
function updateVersionElements() {
    const version = CONFIG.version;
    const githubUser = CONFIG.githubUser;
    const repoName = CONFIG.repoName;
    
    // Función helper para reemplazar placeholders
    function replacePlaceholders(text) {
        return text.replace(/\{\{VERSION\}\}/g, version)
                  .replace(/\{\{GITHUB_USER\}\}/g, githubUser)
                  .replace(/\{\{REPO_NAME\}\}/g, repoName);
    }
    
    // Actualizar todos los enlaces y textos que contengan placeholders
    document.querySelectorAll('a[href*="{{VERSION}}"]').forEach(link => {
        link.href = replacePlaceholders(link.href);
    });
    
    document.querySelectorAll('code').forEach(code => {
        if (code.textContent.includes('{{VERSION}}')) {
            code.textContent = replacePlaceholders(code.textContent);
        }
    });
    
    // Actualizar código de instalación
    document.querySelectorAll('pre code').forEach(code => {
        if (code.textContent.includes('{{VERSION}}')) {
            code.textContent = replacePlaceholders(code.textContent);
        }
    });
    
    // Agregar versión al footer
    const footerBottom = document.querySelector('.footer-bottom p');
    if (footerBottom && !footerBottom.textContent.includes('v')) {
        footerBottom.innerHTML = `&copy; 2024 Floating CheatSheets v${version}. Código abierto bajo licencia MIT.`;
    }
    
    // Agregar badge de versión al hero
    const heroContent = document.querySelector('.hero-content');
    if (heroContent && !document.querySelector('.version-badge')) {
        const versionBadge = document.createElement('div');
        versionBadge.className = 'version-badge';
        versionBadge.innerHTML = `<span class="badge">v${version}</span>`;
        heroContent.insertBefore(versionBadge, heroContent.firstChild);
    }
}

// Navegación suave
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Menú hamburguesa para móviles
function initMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
        
        // Cerrar menú al hacer click en un enlace
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
    }
}

// Animaciones al hacer scroll
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);
    
    // Observar elementos que queremos animar
    document.querySelectorAll('.feature-card, .usage-item, .install-option').forEach(el => {
        observer.observe(el);
    });
}

// Header con efecto al hacer scroll
function initHeaderScroll() {
    const header = document.querySelector('.header');
    if (!header) return;
    
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        // Ocultar/mostrar header al hacer scroll
        if (scrollTop > lastScrollTop && scrollTop > 200) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
    });
}

// Copiar código al clipboard
function initCodeCopy() {
    document.querySelectorAll('.code-block').forEach(codeBlock => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerHTML = '📋 Copiar';
        copyBtn.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.8rem;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        codeBlock.style.position = 'relative';
        codeBlock.appendChild(copyBtn);
        
        codeBlock.addEventListener('mouseenter', () => {
            copyBtn.style.opacity = '1';
        });
        
        codeBlock.addEventListener('mouseleave', () => {
            copyBtn.style.opacity = '0';
        });
        
        copyBtn.addEventListener('click', async () => {
            const code = codeBlock.querySelector('pre code').textContent;
            try {
                await navigator.clipboard.writeText(code);
                copyBtn.innerHTML = '✅ Copiado';
                setTimeout(() => {
                    copyBtn.innerHTML = '📋 Copiar';
                }, 2000);
            } catch (err) {
                console.error('Error al copiar:', err);
            }
        });
    });
}

// Detectar sistema operativo y destacar descarga apropiada
function initOSDetection() {
    const userAgent = navigator.userAgent.toLowerCase();
    const isWindows = userAgent.includes('windows');
    const isLinux = userAgent.includes('linux');
    
    if (isWindows) {
        const windowsBtn = document.querySelector('.windows-btn');
        if (windowsBtn) {
            windowsBtn.classList.add('recommended');
            windowsBtn.insertAdjacentHTML('afterbegin', '<span class="recommended-badge">Recomendado</span>');
        }
    } else if (isLinux) {
        const linuxBtn = document.querySelector('.linux-btn');
        if (linuxBtn) {
            linuxBtn.classList.add('recommended');
            linuxBtn.insertAdjacentHTML('afterbegin', '<span class="recommended-badge">Recomendado</span>');
        }
    }
}

// Inicializar todo cuando se carga la página
document.addEventListener('DOMContentLoaded', async () => {
    await loadVersion();
    initSmoothScrolling();
    initMobileMenu();
    initScrollAnimations();
    initHeaderScroll();
    initCodeCopy();
    initOSDetection();
});

// Actualizar versión cuando se actualice el archivo
window.addEventListener('focus', () => {
    loadVersion();
});