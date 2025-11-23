/**
 * UX Enhancements JavaScript
 * Implementa funcionalidades modernas de UX
 * Basado en Nielsen Norman Group, Material Design y mejores prácticas
 */

(function() {
    'use strict';

    // ============================================
    // 1. LAZY LOADING DE IMÁGENES
    // ============================================
    function initLazyLoading() {
        const lazyImages = document.querySelectorAll('.lazy-load');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        
                        // Si tiene data-src, cargarlo
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                        }
                        
                        // Si tiene data-srcset, cargarlo
                        if (img.dataset.srcset) {
                            img.srcset = img.dataset.srcset;
                        }
                        
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px' // Comenzar a cargar 50px antes de que entre en viewport
            });
            
            lazyImages.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback para navegadores antiguos
            lazyImages.forEach(img => {
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                }
                img.classList.add('loaded');
            });
        }
    }

    // ============================================
    // 2. SCROLL TO TOP BUTTON
    // ============================================
    function initScrollToTop() {
        let scrollToTopBtn = document.getElementById('scrollToTop');
        
        // Crear el botón si no existe
        if (!scrollToTopBtn) {
            scrollToTopBtn = document.createElement('button');
            scrollToTopBtn.id = 'scrollToTop';
            scrollToTopBtn.className = 'scroll-to-top';
            scrollToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
            scrollToTopBtn.setAttribute('aria-label', 'Scroll to top');
            document.body.appendChild(scrollToTopBtn);
        }
        
        // Mostrar/ocultar botón según scroll
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.classList.add('visible');
            } else {
                scrollToTopBtn.classList.remove('visible');
            }
        });
        
        // Funcionalidad de scroll
        scrollToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // ============================================
    // 3. SMOOTH SCROLL PARA ENLACES INTERNOS
    // ============================================
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                
                // Ignorar # solo
                if (href === '#') return;
                
                const targetElement = document.querySelector(href);
                
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // ============================================
    // 4. SKELETON SCREENS
    // ============================================
    function showSkeletons(containerId, duration = 1000) {
        const skeleton = document.getElementById(`skeleton${containerId}`);
        const content = document.getElementById(containerId);
        
        if (skeleton && content) {
            skeleton.style.display = 'flex';
            content.style.display = 'none';
            
            setTimeout(() => {
                skeleton.style.display = 'none';
                content.style.display = 'flex';
            }, duration);
        }
    }

    // ============================================
    // 5. ADD TO CART ANIMATION
    // ============================================
    function initAddToCartAnimation() {
        const addToCartForms = document.querySelectorAll('.add-to-cart-form');
        
        addToCartForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const button = this.querySelector('.add-to-cart-btn');
                
                if (button && !button.disabled && !button.classList.contains('success')) {
                    button.classList.add('success');
                    
                    // Añadir efecto al contador del carrito
                    const cartBadge = document.querySelector('.cart-badge, .badge');
                    if (cartBadge) {
                        cartBadge.classList.add('pulse');
                        setTimeout(() => {
                            cartBadge.classList.remove('pulse');
                        }, 1000);
                    }
                    
                    // Reset después de 2.5 segundos
                    setTimeout(() => {
                        button.classList.remove('success');
                    }, 2500);
                }
            });
        });
    }

    // ============================================
    // 6. TOAST NOTIFICATIONS
    // ============================================
    function showToast(message, type = 'info', duration = 3000) {
        // Crear contenedor si no existe
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
            `;
            document.body.appendChild(toastContainer);
        }
        
        // Crear toast
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-modern fade-in`;
        toast.style.cssText = `
            min-width: 300px;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-times-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        toast.innerHTML = `
            <i class="fas ${icons[type] || icons.info} me-2"></i>
            ${message}
            <button type="button" class="btn-close float-end" aria-label="Close"></button>
        `;
        
        toastContainer.appendChild(toast);
        
        // Close button
        toast.querySelector('.btn-close').addEventListener('click', () => {
            toast.remove();
        });
        
        // Auto remove
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    // ============================================
    // 7. FORM VALIDATION FEEDBACK
    // ============================================
    function initFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                let isValid = true;
                
                // Validar campos requeridos
                const requiredFields = this.querySelectorAll('[required]');
                requiredFields.forEach(field => {
                    if (!field.value.trim()) {
                        isValid = false;
                        field.classList.add('is-invalid');
                        
                        // Agregar mensaje de error si no existe
                        if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('invalid-feedback')) {
                            const feedback = document.createElement('div');
                            feedback.className = 'invalid-feedback';
                            feedback.textContent = field.dataset.errorMessage || 'This field is required';
                            field.parentNode.insertBefore(feedback, field.nextSibling);
                        }
                    } else {
                        field.classList.remove('is-invalid');
                        const feedback = field.nextElementSibling;
                        if (feedback && feedback.classList.contains('invalid-feedback')) {
                            feedback.remove();
                        }
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    showToast('Please fill in all required fields', 'warning');
                }
            });
        });
    }

    // ============================================
    // 8. DEBOUNCE UTILITY
    // ============================================
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // ============================================
    // 9. SEARCH AUTOCOMPLETE
    // ============================================
    function initSearchAutocomplete() {
        const searchInputs = document.querySelectorAll('input[data-autocomplete]');
        
        searchInputs.forEach(input => {
            const resultsContainer = document.createElement('div');
            resultsContainer.className = 'autocomplete-results';
            resultsContainer.style.cssText = `
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 1px solid #e5e7eb;
                border-top: none;
                border-radius: 0 0 8px 8px;
                max-height: 300px;
                overflow-y: auto;
                display: none;
                z-index: 1000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            `;
            
            input.parentElement.style.position = 'relative';
            input.parentElement.appendChild(resultsContainer);
            
            const searchHandler = debounce(async (query) => {
                if (query.length < 2) {
                    resultsContainer.style.display = 'none';
                    return;
                }
                
                try {
                    const url = input.dataset.autocomplete;
                    const response = await fetch(`${url}?q=${encodeURIComponent(query)}`);
                    const results = await response.json();
                    
                    if (results.length > 0) {
                        resultsContainer.innerHTML = results.map(item => `
                            <a href="${item.url}" class="autocomplete-item" style="
                                display: block;
                                padding: 12px 16px;
                                text-decoration: none;
                                color: #1f2937;
                                border-bottom: 1px solid #f3f4f6;
                                transition: background 0.2s;
                            ">
                                ${item.name}
                            </a>
                        `).join('');
                        
                        resultsContainer.style.display = 'block';
                        
                        // Hover effects
                        resultsContainer.querySelectorAll('.autocomplete-item').forEach(item => {
                            item.addEventListener('mouseenter', function() {
                                this.style.background = '#f9fafb';
                            });
                            item.addEventListener('mouseleave', function() {
                                this.style.background = 'white';
                            });
                        });
                    } else {
                        resultsContainer.style.display = 'none';
                    }
                } catch (error) {
                    console.error('Autocomplete error:', error);
                }
            }, 300);
            
            input.addEventListener('input', (e) => searchHandler(e.target.value));
            
            // Cerrar al hacer click fuera
            document.addEventListener('click', (e) => {
                if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
                    resultsContainer.style.display = 'none';
                }
            });
        });
    }

    // ============================================
    // 10. RIPPLE EFFECT
    // ============================================
    function initRippleEffect() {
        document.querySelectorAll('.btn-ripple').forEach(button => {
            button.addEventListener('click', function(e) {
                const rect = this.getBoundingClientRect();
                const ripple = document.createElement('span');
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.6);
                    left: ${x}px;
                    top: ${y}px;
                    transform: scale(0);
                    animation: ripple 0.6s ease-out;
                    pointer-events: none;
                `;
                
                this.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            });
        });
    }

    // ============================================
    // 11. PERFORMANCE OBSERVER
    // ============================================
    function monitorPerformance() {
        if ('PerformanceObserver' in window) {
            // Core Web Vitals
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    console.log(`${entry.name}: ${entry.value}ms`);
                }
            });
            
            try {
                observer.observe({ entryTypes: ['navigation', 'paint', 'largest-contentful-paint'] });
            } catch (e) {
                console.warn('Performance monitoring not supported');
            }
        }
    }

    // ============================================
    // 12. INICIALIZACIÓN
    // ============================================
    function init() {
        // Esperar a que el DOM esté completamente cargado
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        console.log('🎨 UX Enhancements initialized');
        
        // Inicializar todos los módulos
        initLazyLoading();
        initScrollToTop();
        initSmoothScroll();
        initAddToCartAnimation();
        initFormValidation();
        initSearchAutocomplete();
        initRippleEffect();
        
        // Solo en desarrollo
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            monitorPerformance();
        }
    }

    // Exportar funciones globales
    window.UX = {
        showToast,
        showSkeletons,
        debounce
    };

    // Auto-inicializar
    init();

})();

// ============================================
// CSS PARA RIPPLE ANIMATION
// ============================================
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
