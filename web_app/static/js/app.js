// CHRONOS-EYE Web - Frontend Logic

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;

        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
    });
});

// Load stats on page load
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        document.getElementById('stats').textContent =
            `Database: ${data.total_items} media entries • ${data.embedding_dim}-dim`;
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Search
document.getElementById('search-btn').addEventListener('click', async () => {
    const query = document.getElementById('search-input').value.trim();
    if (!query) return;

    const btn = document.getElementById('search-btn');
    const status = document.getElementById('search-status');
    const resultsDiv = document.getElementById('results');

    btn.disabled = true;
    btn.textContent = 'Searching...';
    status.textContent = 'AI is searching... 🧠';
    status.className = 'status';
    resultsDiv.innerHTML = '';

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, top_k: 20, min_score: 0.2 })
        });

        if (!response.ok) throw new Error('Search failed');

        const data = await response.json();

        if (data.count === 0) {
            status.textContent = `No results found for "${query}"`;
            status.className = 'status error';
        } else {
            displayResults(data.results);
            status.textContent = `Found ${data.count} matches`;
            status.className = 'status success';
        }
    } catch (error) {
        status.textContent = `Error: ${error.message}`;
        status.className = 'status error';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Search Locally';
    }
});

function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    results.forEach(result => {
        const card = document.createElement('div');
        card.className = 'result-card';
        card.onclick = () => openFile(result.id);

        card.innerHTML = `
            <img src="/api/thumbnail/${result.id}" class="result-thumbnail" alt="Thumbnail">
            <div class="result-score">${result.score}%</div>
            <div class="result-filename">${result.filename}</div>
            <div class="result-path">${result.path}</div>
        `;

        resultsDiv.appendChild(card);
    });
}

async function openFile(fileId) {
    try {
        await fetch(`/api/open/${fileId}`);
    } catch (error) {
        console.error('Failed to open file:', error);
    }
}

// Folder picker
document.getElementById('browse-btn').addEventListener('click', () => {
    document.getElementById('folder-picker').click();
});

document.getElementById('folder-picker').addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        // Get the path from the first file
        const firstFile = e.target.files[0];
        // Extract folder path (remove filename)
        const fullPath = firstFile.webkitRelativePath || firstFile.path || firstFile.name;
        const folderPath = fullPath.split('/')[0] || fullPath.split('\\')[0];

        // For Windows, try to construct full path if available
        if (firstFile.path) {
            const pathParts = firstFile.path.split(/[/\\]/);
            pathParts.pop(); // Remove filename
            document.getElementById('folder-path').value = pathParts.join('\\');
        } else {
            // Fallback: show relative path and ask user to complete it
            document.getElementById('folder-path').value = folderPath + ' (Please complete full path)';
        }
    }
});

// Indexing
document.getElementById('index-btn').addEventListener('click', async () => {
    const folderPath = document.getElementById('folder-path').value.trim();
    if (!folderPath) {
        alert('Please enter a folder path');
        return;
    }

    const incremental = document.getElementById('index-mode').value === 'true';
    const quantization = document.getElementById('vram-quant').value;

    const btn = document.getElementById('index-btn');
    const status = document.getElementById('index-status');
    const progressBar = document.getElementById('progress-bar');

    btn.disabled = true;
    status.textContent = 'Starting indexing...';
    status.className = 'status';

    try {
        const response = await fetch('/api/index', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ folder_path: folderPath, incremental, quantization })
        });

        if (!response.ok) throw new Error('Failed to start indexing');

        // Poll for progress
        const progressInterval = setInterval(async () => {
            const progressRes = await fetch('/api/progress');
            const progress = await progressRes.json();

            progressBar.style.width = `${progress.progress}%`;
            status.textContent = progress.message;

            if (!progress.active) {
                clearInterval(progressInterval);
                btn.disabled = false;
                status.className = progress.message.includes('Error') ? 'status error' : 'status success';
                loadStats(); // Reload stats
            }
        }, 1000);
    } catch (error) {
        status.textContent = `Error: ${error.message}`;
        status.className = 'status error';
        btn.disabled = false;
    }
});

// Search on Enter key
document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('search-btn').click();
    }
});

// Initial load
loadStats();
