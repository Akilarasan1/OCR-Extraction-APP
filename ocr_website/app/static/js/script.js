// DOM Elements
const fileInput = document.getElementById('fileInput');
const extractBtn = document.getElementById('extractBtn');
const clearBtn = document.getElementById('clearBtn');
const downloadBtn = document.getElementById('downloadBtn');
const filePreview = document.getElementById('filePreview');
const resultText = document.getElementById('resultText');
const loadingIndicator = document.getElementById('loadingIndicator');
const copyBtn = document.getElementById('copyBtn');
const uploadSection = document.getElementById('uploadSection');

fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;

    // Enable buttons
    extractBtn.disabled = false;
    clearBtn.disabled = false;

    // Show preview
    showFilePreview(file);
});

function showFilePreview(file) {
    filePreview.innerHTML = '';
    
    if (file.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        filePreview.appendChild(img);
    } else if (file.type === 'application/pdf') {
        const embed = document.createElement('embed');
        embed.src = URL.createObjectURL(file);
        embed.type = 'application/pdf';
        embed.style.width = '100%';
        embed.style.height = '500px';
        filePreview.appendChild(embed);
    } else {
        filePreview.innerHTML = `<p>Preview not available for ${file.name}</p>`;
    }
}

// Single Extract text event listener with language support
extractBtn.addEventListener('click', async function() {
    const file = fileInput.files[0];
    if (!file) return;

    loadingIndicator.style.display = 'block';
    extractBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('file', file);
        
        // Get selected language (default to English if not selected)
        const language = document.getElementById('languageSelect').value || 'en';
        
        const response = await fetch(`/api/extract?lang=${encodeURIComponent(language)}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
             const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || errorData.message || 'Extraction failed');
        }

        const data = await response.json();
        resultText.value = data.text;
        downloadBtn.disabled = false;
        
    } catch (error) {
        resultText.value = `Error: ${error.message}`;
        console.error('Extraction error:', error);
    } finally {
        loadingIndicator.style.display = 'none';
        extractBtn.disabled = false;
    }
});

// Clear everything
clearBtn.addEventListener('click', function() {
    fileInput.value = '';
    filePreview.innerHTML = '';
    resultText.value = '';
    extractBtn.disabled = true;
    clearBtn.disabled = true;
    downloadBtn.disabled = true;
});

// Download text
downloadBtn.addEventListener('click', function() {
    if (!resultText.value) return;

    const blob = new Blob([resultText.value], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'extracted_text.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});



// Modified extractBtn click handler
extractBtn.addEventListener('click', async function() {
    const file = fileInput.files[0];
    if (!file) return;

    // Clear previous results immediately
    resultText.value = '';
    copyBtn.disabled = true;
    downloadBtn.disabled = true;
    
    loadingIndicator.style.display = 'block';
    extractBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const language = document.getElementById('languageSelect').value || 'en';
        
        const response = await fetch(`/api/extract?lang=${encodeURIComponent(language)}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        const data = await response.json();
        resultText.value = data.text;
        downloadBtn.disabled = false;
        copyBtn.disabled = false;
        
    } catch (error) {
        resultText.value = `Error: ${error.message}`;
        console.error('Extraction error:', error);
    } finally {
        loadingIndicator.style.display = 'none';
        extractBtn.disabled = false;
    }
});

// New copy button functionality
copyBtn.addEventListener('click', function() {
    if (!resultText.value) return;
    
    resultText.select();
    document.execCommand('copy');
    
    // Visual feedback
    const originalText = copyBtn.innerHTML;
    copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
    copyBtn.style.backgroundColor = '#28a745';
    
    setTimeout(() => {
        copyBtn.innerHTML = originalText;
        copyBtn.style.backgroundColor = '#6c757d';
    }, 2000);
});

// Clear button should also disable copy button
clearBtn.addEventListener('click', function() {
    fileInput.value = '';
    filePreview.innerHTML = '';
    resultText.value = '';
    extractBtn.disabled = true;
    clearBtn.disabled = true;
    downloadBtn.disabled = true;
    copyBtn.disabled = true;

});


// Prevent default behaviors for drag/drop
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadSection.addEventListener(eventName, e => e.preventDefault());
    document.body.addEventListener(eventName, e => e.preventDefault());
});

// Highlight drop area
['dragenter', 'dragover'].forEach(eventName => {
    uploadSection.addEventListener(eventName, () => {
        uploadSection.classList.add('drag-over');
    });
});

['dragleave', 'drop'].forEach(eventName => {
    uploadSection.addEventListener(eventName, () => {
        uploadSection.classList.remove('drag-over');
    });
});

// Handle dropped files
uploadSection.addEventListener('drop', e => {
    const file = e.dataTransfer.files[0];
    if (file) {
        fileInput.files = e.dataTransfer.files; // So the existing logic still works
        showFilePreview(file);
        extractBtn.disabled = false;
        clearBtn.disabled = false;
    }
});



