document.getElementById('bot-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const semester = document.getElementById('semester').value;
    const sections = document.getElementById('sections').value;

    // Trigger UI transition (Vercel-like morph)
    const inputCard = document.getElementById('input-card');
    const processCard = document.getElementById('process-card');
    
    inputCard.style.opacity = '0';
    inputCard.style.transform = 'translate(-50%, -60%) scale(0.95)';
    
    setTimeout(() => {
        inputCard.classList.add('hidden');
        processCard.classList.remove('hidden');
        processCard.style.opacity = '1';
        processCard.style.transform = 'translate(-50%, -50%) scale(1)';
        processCard.style.pointerEvents = 'all';
    }, 400);

    // Send start command to backend
    await fetch('/api/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, semester, sections })
    });

    // Start listening to Server-Sent Events (SSE)
    const eventSource = new EventSource('/stream');
    const terminal = document.getElementById('terminal');
    const progressBar = document.getElementById('progress-bar');
    const statusText = document.getElementById('status-text');

    let progress = 10;
    progressBar.style.width = `${progress}%`;

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        // Append log to terminal
        const div = document.createElement('div');
        div.className = `log-entry log-${data.status}`;
        div.textContent = `> ${data.message}`;
        terminal.appendChild(div);
        
        // Auto-scroll terminal
        terminal.scrollTop = terminal.scrollHeight;

        // Update pseudo-progress bar
        if (progress < 90) {
            progress += Math.random() * 15;
            progressBar.style.width = `${progress}%`;
        }
        
        statusText.textContent = data.message;

        if (data.status === 'done') {
            eventSource.close();
            progressBar.style.width = '100%';
            
            // Final success state
            document.querySelector('.pulse-ring').style.animation = 'none';
            document.querySelector('.pulse-ring').style.borderColor = '#32d74b';
            
            setTimeout(() => {
                statusText.textContent = "Execution Complete.";
                statusText.style.color = "#32d74b";
            }, 500);
        }
    };
});
