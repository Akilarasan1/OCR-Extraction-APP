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

// File input handler
fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;
    handleFileSelection(file);
});

function handleFileSelection(file) {
    extractBtn.disabled = false;
    clearBtn.disabled = false;
    showFilePreview(file);
}

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

// Single extract button handler
extractBtn.addEventListener('click', async function(e) {
    e.stopPropagation();
    e.preventDefault();
    
    const file = fileInput.files[0];
    if (!file) return;

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

        if (!response.ok) throw new Error(await response.text());
        
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

// Drag and drop implementation
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadSection.addEventListener(eventName, e => {
        e.preventDefault();
        e.stopPropagation();
        if (eventName === 'drop') {
            const files = e.dataTransfer.files;
            if (files.length) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change'));
            }
        } else {
            uploadSection.classList.toggle('drag-over', 
                eventName === 'dragenter' || eventName === 'dragover');
        }
    }, { passive: false });
});


clearBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    
    // Reset file input
    fileInput.value = '';
    
    // Clear preview and results
    filePreview.innerHTML = '';
    resultText.value = '';
    
    // Disable all action buttons
    [extractBtn, clearBtn, downloadBtn, copyBtn].forEach(btn => {
        btn.disabled = true;
    });
    
    // Reset drag-over state if active
    uploadSection.classList.remove('drag-over');
});


downloadBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    
    if (!resultText.value) return;

    try {
        const blob = new Blob([resultText.value], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `extracted_${new Date().getTime()}.txt`; // Unique filename
        a.style.display = 'none';
        
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
    } catch (error) {
        console.error('Download failed:', error);
        resultText.value = `Download Error: ${error.message}\n\n${resultText.value}`;
    }
});



copyBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    
    if (!resultText.value) return;
    
    try {
        // Modern clipboard API (preferred)
        if (navigator.clipboard) {
            navigator.clipboard.writeText(resultText.value)
                .then(() => showCopyFeedback())
                .catch(err => console.error('Clipboard error:', err));
        } 
        // Fallback for older browsers
        else {
            resultText.select();
            document.execCommand('copy');
            showCopyFeedback();
        }
    } catch (error) {
        console.error('Copy failed:', error);
    }
});

function showCopyFeedback() {
    const originalHTML = copyBtn.innerHTML;
    const originalBg = copyBtn.style.backgroundColor;
    
    copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
    copyBtn.style.backgroundColor = '#28a745';
    
    setTimeout(() => {
        copyBtn.innerHTML = originalHTML;
        copyBtn.style.backgroundColor = originalBg;
    }, 2000);
}


// Unified drag-and-drop handlers
const handleDragEvent = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'drop') {
        const files = e.dataTransfer.files;
        if (files.length) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change'));
        }
    }
    
    uploadSection.classList.toggle(
        'drag-over',
        e.type === 'dragenter' || e.type === 'dragover'
    );
};

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadSection.addEventListener(eventName, handleDragEvent);
});



// Reset drag state if user drags outside window
window.addEventListener('dragleave', (e) => {
    if (e.clientX <= 0 || e.clientY <= 0 
        || e.clientX >= window.innerWidth 
        || e.clientY >= window.innerHeight) {
        uploadSection.classList.remove('drag-over');
    }
});
