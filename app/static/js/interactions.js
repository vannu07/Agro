/* ===================================
   KRISHI MITR - INTERACTIVE SCRIPTS
   =================================== */

// Navbar scroll effect
window.addEventListener('scroll', function() {
  const navbar = document.querySelector('.navbar-elite');
  if (navbar) {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }
});

// Page fade-in animation
document.addEventListener('DOMContentLoaded', function() {
  const pageContent = document.getElementById('page-content');
  const eliteLoader = document.getElementById('elite-loader');
  
  if (eliteLoader) {
    setTimeout(() => {
      eliteLoader.classList.add('hidden');
    }, 1500);
  }
  
  if (pageContent) {
    pageContent.style.opacity = '1';
  }
});

// Form validation
function validateForm(formElement) {
  const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
  let isValid = true;
  
  inputs.forEach(input => {
    if (!input.value.trim()) {
      input.classList.add('error');
      const errorMsg = document.createElement('div');
      errorMsg.className = 'form-error';
      errorMsg.textContent = 'This field is required';
      input.parentNode.appendChild(errorMsg);
      isValid = false;
    } else {
      input.classList.remove('error');
    }
  });
  
  return isValid;
}

// Input focus effects
document.querySelectorAll('input, textarea, select').forEach(input => {
  input.addEventListener('focus', function() {
    this.style.borderColor = 'var(--primary-emerald)';
    this.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1)';
  });
  
  input.addEventListener('blur', function() {
    this.style.borderColor = 'var(--neutral-light-gray)';
    this.style.boxShadow = 'none';
  });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// Card hover effects
document.querySelectorAll('.card, .agent-card').forEach(card => {
  card.addEventListener('mouseenter', function() {
    this.style.transform = 'translateY(-4px)';
  });
  
  card.addEventListener('mouseleave', function() {
    this.style.transform = 'translateY(0)';
  });
});

// Button ripple effect
function createRipple(event) {
  const button = event.currentTarget;
  const ripple = document.createElement('span');
  
  const rect = button.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  const x = event.clientX - rect.left - size / 2;
  const y = event.clientY - rect.top - size / 2;
  
  ripple.style.width = ripple.style.height = size + 'px';
  ripple.style.left = x + 'px';
  ripple.style.top = y + 'px';
  ripple.classList.add('ripple');
  
  button.appendChild(ripple);
  
  setTimeout(() => ripple.remove(), 600);
}

document.querySelectorAll('button, .btn').forEach(button => {
  button.addEventListener('click', createRipple);
});

// Counter animation
function animateCounter(element, target, duration = 2000) {
  let current = 0;
  const increment = target / (duration / 50);
  
  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      element.textContent = target;
      clearInterval(timer);
    } else {
      element.textContent = Math.floor(current);
    }
  }, 50);
}

// Intersection Observer for scroll animations
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-fade-in-up');
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll('.agent-card, .feature-card, .card').forEach(element => {
  observer.observe(element);
});

// Modal functionality
class Modal {
  constructor(modalElement) {
    this.modal = modalElement;
    this.closeBtn = modalElement.querySelector('[data-close]');
    this.init();
  }
  
  init() {
    if (this.closeBtn) {
      this.closeBtn.addEventListener('click', () => this.close());
    }
    
    this.modal.addEventListener('click', (e) => {
      if (e.target === this.modal) this.close();
    });
  }
  
  open() {
    this.modal.style.display = 'flex';
    this.modal.classList.add('animate-fade-in');
  }
  
  close() {
    this.modal.classList.add('animate-fade-out');
    setTimeout(() => {
      this.modal.style.display = 'none';
      this.modal.classList.remove('animate-fade-out');
    }, 300);
  }
}

// Tabs functionality
class Tabs {
  constructor(containerElement) {
    this.container = containerElement;
    this.tabs = containerElement.querySelectorAll('[role="tab"]');
    this.panels = containerElement.querySelectorAll('[role="tabpanel"]');
    this.init();
  }
  
  init() {
    this.tabs.forEach(tab => {
      tab.addEventListener('click', (e) => this.selectTab(e.currentTarget));
    });
  }
  
  selectTab(tab) {
    this.tabs.forEach(t => t.setAttribute('aria-selected', 'false'));
    this.panels.forEach(p => p.style.display = 'none');
    
    tab.setAttribute('aria-selected', 'true');
    const panelId = tab.getAttribute('aria-controls');
    const panel = document.getElementById(panelId);
    if (panel) {
      panel.style.display = 'block';
      panel.classList.add('animate-fade-in');
    }
  }
}

// Tooltip functionality
function initTooltips() {
  document.querySelectorAll('[data-tooltip]').forEach(element => {
    element.addEventListener('mouseenter', function() {
      const tooltip = document.createElement('div');
      tooltip.className = 'tooltip';
      tooltip.textContent = this.getAttribute('data-tooltip');
      document.body.appendChild(tooltip);
      
      const rect = this.getBoundingClientRect();
      tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
      tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
      
      setTimeout(() => tooltip.classList.add('show'), 10);
      
      this.addEventListener('mouseleave', () => {
        tooltip.remove();
      }, { once: true });
    });
  });
}

// Debounce function
function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// Lazy load images
if ('IntersectionObserver' in window) {
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.add('loaded');
        imageObserver.unobserve(img);
      }
    });
  });
  
  document.querySelectorAll('img[data-src]').forEach(img => imageObserver.observe(img));
}

// Theme toggle
function toggleTheme() {
  const root = document.documentElement;
  const currentTheme = root.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  root.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  // Check saved theme
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  
  // Initialize tooltips
  initTooltips();
  
  // Initialize any modals
  document.querySelectorAll('[role="dialog"]').forEach(modal => {
    new Modal(modal);
  });
  
  // Initialize any tabs
  document.querySelectorAll('[role="tablist"]').forEach(tablist => {
    new Tabs(tablist);
  });
});

// Export for use in other scripts
window.KrishiMitr = {
  Modal,
  Tabs,
  validateForm,
  animateCounter,
  debounce,
  toggleTheme
};
