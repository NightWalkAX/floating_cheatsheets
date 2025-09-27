// Configuración global
const CONFIG = {
    githubUser: 'NightWalkAX',
    repoName: 'floating_cheatsheets',
    releaseInfo: null
};

// Cargar información de la release dinámicamente
async function loadReleaseInfo() {
    try {
        const response = await fetch('./release_info.json?t=' + new Date().getTime());
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        CONFIG.releaseInfo = data;
        updateDynamicContent();
    } catch (error) {
        console.error('No se pudo cargar la información de la release:', error);
        // Fallback a contenido por defecto si falla la carga
        CONFIG.releaseInfo = {
            version: 'N/A',
            windowsURL: '#',
            linuxURL: '#'
        };
        updateDynamicContent();
    }
}

// Actualizar todos los elementos dinámicos en la página
function updateDynamicContent() {
    const { version, windowsURL, linuxURL } = CONFIG.releaseInfo;
    const githubUser = CONFIG.githubUser;
    const repoName = CONFIG.repoName;

    // Actualizar enlaces de descarga principales
    const linuxLink = document.getElementById('linux-download-link');
    if (linuxLink) linuxLink.href = linuxURL;

    const windowsLink = document.getElementById('windows-download-link');
    if (windowsLink) windowsLink.href = windowsURL;

    // Función helper para reemplazar placeholders de versión
    function replaceVersionPlaceholder(text) {
        return text.replace(/\{\{VERSION\}\}/g, version);
    }

    // Actualizar placeholders en el texto de instalación y otros lugares
    document.querySelectorAll('code, .install-option, a[href*="floating-cheatsheets_"]').forEach(element => {
        if (element.href && element.href.includes('floating-cheatsheets_')) {
            // Caso especial para el enlace de instalación de Linux
            const simpleLinuxName = `floating-cheatsheets_${version}_all.deb`;
            element.href = `https://github.com/${githubUser}/${repoName}/releases/latest/download/${simpleLinuxName}`;
        }
        if (element.textContent && element.textContent.includes('{{VERSION}}')) {
            element.textContent = replaceVersionPlaceholder(element.textContent);
        }
    });

    // Actualizar versión en el footer
    const footerBottom = document.querySelector('.footer-bottom p');
    if (footerBottom && !footerBottom.textContent.includes(`v${version}`)) {
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
    await loadReleaseInfo();
    initSmoothScrolling();
    initMobileMenu();
    initScrollAnimations();
    initHeaderScroll();
    initCodeCopy();
    initOSDetection();
});

// Actualizar información de la release cuando la ventana vuelve a tener foco
window.addEventListener('focus', () => {
    loadReleaseInfo();
});