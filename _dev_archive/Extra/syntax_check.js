addEventListener("load", function () {
			setTimeout(hideURLbar, 0);
		}, false);

		function hideURLbar() {
			window.scrollTo(0, 1);
		}





















const themeToggle = document.getElementById('theme-toggle');
		const darkIcon = document.getElementById('theme-toggle-dark-icon');
		const lightIcon = document.getElementById('theme-toggle-light-icon');
		
		// Initial check
		if (localStorage.getItem('theme') === 'light') {
			document.documentElement.setAttribute('data-theme', 'light');
			darkIcon.classList.add('d-none');
			lightIcon.classList.remove('d-none');
		}

		themeToggle.addEventListener('click', () => {
			const currentTheme = document.documentElement.getAttribute('data-theme');
			if (currentTheme === 'light') {
				document.documentElement.removeAttribute('data-theme');
				localStorage.setItem('theme', 'dark');
				darkIcon.classList.remove('d-none');
				lightIcon.classList.add('d-none');
			} else {
				document.documentElement.setAttribute('data-theme', 'light');
				localStorage.setItem('theme', 'light');
				darkIcon.classList.add('d-none');
				lightIcon.classList.remove('d-none');
			}
		});

/* Premium Chatbot Logic */
    function togglePremiumChat() {
        const box = document.getElementById('chat-box');
        if (box.style.display === 'flex') {
            box.style.display = 'none';
        } else {
            box.style.display = 'flex';
            document.getElementById('chatInput').focus();
        }
    }
    
    let chatHistory = [];

    function scrollToBottom() {
        const chatWindow = document.getElementById('chatWindow');
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function handleKeyPress(e) {
        if (e.key === 'Enter') sendMessage();
    }

    function fillSuggestion(text) {
        document.getElementById('chatInput').value = text;
        sendMessage();
    }

    async function sendMessage() {
        const input = document.getElementById('chatInput');
        const text = input.value.trim();
        if (!text) return;
        
        input.value = '';
        const chips = document.getElementById('suggestionChips');
        if (chips) chips.style.display = 'none';
        
        document.getElementById('chatWindow').insertAdjacentHTML('beforeend', `
            <div class="message user">
                <div class="message-avatar">U</div>
                <div class="bubble">${text}</div>
            </div>
        `);
        scrollToBottom();
        
        const typingId = 'typing-' + Date.now();
        document.getElementById('chatWindow').insertAdjacentHTML('beforeend', `
            <div class="message bot" id="${typingId}">
                <div class="message-avatar">
                   <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/>
                        <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
                    </svg>
                </div>
                <div class="bubble">...</div>
            </div>
        `);
        scrollToBottom();
        
        try {
            const response = await fetch('/api/chatbot/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: text, history: chatHistory })
            });
            
            document.getElementById(typingId).remove();
            
            const msgId = 'bot-' + Date.now();
            document.getElementById('chatWindow').insertAdjacentHTML('beforeend', `
                <div class="message bot">
                    <div class="message-avatar">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/>
                            <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
                        </svg>
                    </div>
                    <div class="bubble" id="${msgId}"></div>
                </div>
            `);
            const bubble = document.getElementById(msgId);
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let botResponse = "";
            
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\\n');
                for (let line of lines) {
                    if (line.startsWith('data: ')) {
                        const dataStr = line.replace('data: ', '').trim();
                        if (dataStr === '[DONE]') break;
                        if (dataStr) {
                            try {
                                const dataObj = JSON.parse(dataStr);
                                if (dataObj.token) botResponse += dataObj.token;
                                if (dataObj.error) botResponse = dataObj.error;
                                bubble.innerText = botResponse;
                                scrollToBottom();
                            } catch (e) {}
                        }
                    }
                }
            }
            chatHistory.push({ human: text, ai: botResponse });
        } catch (err) {
            document.getElementById(typingId).remove();
            document.getElementById('chatWindow').insertAdjacentHTML('beforeend', `
                <div class="message bot"><div class="bubble">Connection failed. Please try again.</div></div>
            `);
        }
    }

let recognition = null;
if ("SpeechRecognition" in window || "webkitSpeechRecognition" in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.lang = "en-IN";
  recognition.onresult = function(event) {
    const transcript = event.results[0][0].transcript;
    const input = document.getElementById('userInput');
    input.value = transcript;
    sendMessage();
  };
}
function startVoice() {
  if (recognition) { recognition.start(); }
  else { alert("Voice recognition not supported."); }
}
function speakText(text) {
  if (!window.speechSynthesis) return;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-IN";
  window.speechSynthesis.speak(utterance);
}



AOS.init({
    duration: 1000,
    once: true,
  });

  // Navbar Scroll Logic
  window.addEventListener('scroll', () => {
    const nav = document.querySelector('.navbar-elite');
    if (window.scrollY > 50) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  });

  // Initialize on load
  if (window.scrollY > 50) {
    document.querySelector('.navbar-elite').classList.add('scrolled');
  }

// Global applicator for data attributes to satisfy IDE syntax checking
		document.addEventListener('DOMContentLoaded', () => {
			// Apply background images
			document.querySelectorAll('[data-bg-url]').forEach(el => {
				el.style.backgroundImage = `url('${el.getAttribute('data-bg-url')}')`;
			});
			// Apply widths (e.g. for progress bars)
			document.querySelectorAll('[data-width]').forEach(el => {
				el.style.width = el.getAttribute('data-width');
			});
		});

        // LOADER & FADE-IN LOGIC
        window.addEventListener('load', () => {
            const loader = document.getElementById('elite-loader');
            const content = document.getElementById('page-content');
            
            if(loader) {
                loader.style.opacity = '0';
                setTimeout(() => {
                    loader.classList.remove('active');
                    loader.style.display = 'none';
                }, 800);
            }
            
            if(content) {
                content.style.opacity = '1';
            }
            // Initialize AOS
            if (typeof AOS !== 'undefined') {
                AOS.init({
                    duration: 1000,
                    once: true,
                    offset: 100
                });
            }
        });