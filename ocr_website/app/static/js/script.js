// Global variables
let isProcessing = false;

// DOM elements
const imageUploadArea = document.getElementById('image-upload-area');
const pdfUploadArea = document.getElementById('pdf-upload-area');
const imageFileInput = document.getElementById('image-file');
const pdfFileInput = document.getElementById('pdf-file');
const imageResults = document.getElementById('image-results');
const pdfResults = document.getElementById('pdf-results');
const ocrEngine = document.getElementById('ocr-engine');
const language = document.getElementById('language');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeFileUploads();
});

// Tab functionality
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => {
                content.classList.remove('active');
                content.style.display = 'none';
            });
            
            // Add active class to clicked button and show corresponding content
            button.classList.add('active');
            const targetContent = document.getElementById(targetTab);
            targetContent.classList.add('active');
            targetContent.style.display = 'block';
        });
    });
}

// File upload functionality
function initializeFileUploads() {
    setupFileUpload(imageUploadArea, imageFileInput, 'image');  // Image upload
    setupFileUpload(pdfUploadArea, pdfFileInput, 'pdf');     // PDF upload
}

function setupFileUpload(uploadArea, fileInput, type) {
    // Click to upload
    uploadArea.addEventListener('click', () => {
        if (!isProcessing) {
            fileInput.click();}
        });

    // File input change
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFileUpload(file, type);
        }
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const file = e.dataTransfer.files[0];
        if (file && !isProcessing) {
            // Validate file type
            if (type === 'image' && file.type.startsWith('image/')) {
                handleFileUpload(file, type);
            } else if (type === 'pdf' && file.type === 'application/pdf') {
                handleFileUpload(file, type);
            } else {
                showError(type === 'image' ? imageResults : pdfResults, 
                         `Please select a valid ${type} file.`);
            }
        }
    });
}

// Handle file upload
async function handleFileUpload(file, type) {
    if (isProcessing) return;
    
    isProcessing = true;
    const resultsContainer = type === 'image' ? imageResults : pdfResults;
    
    // Show loading state
    showLoading(resultsContainer, type);
    
    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        let url = '';
        if (type === 'image') {
            const engine = ocrEngine.value;
            const lang = language.value;
            url = `/api/ocr/extract?engine=${engine}&lang=${lang}`;
        } else {
            url = '/api/pdf/extract';
        }

        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.status === 'success') {
            showResult(resultsContainer, data, type);
        } else {
            throw new Error(data.message || 'Processing failed');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showError(resultsContainer, error.message);
    } finally {
        isProcessing = false;
    }
}

// Show loading state
function showLoading(container, type) {
    const engineName = type === 'image' ? getEngineName(ocrEngine.value) : 'PDF Processor';
    const loadingText = type === 'image' ? 'Processing Image...' : 'Extracting Text...';
    const description = type === 'image' ? 
        `Extracting text using ${engineName}` : 
        'Processing your PDF document';

    container.innerHTML = `
        <div class="flex items-center justify-center py-12">
            <div class="text-center">
                <div class="loading-spinner mx-auto mb-4"></div>
                <h3 class="text-xl font-semibold text-gray-700 mb-2">${loadingText}</h3>
                <p class="text-gray-500">${description}</p>
            </div>
        </div>
    `;
}

// Show successful result
function showResult(container, data, type) {
    const title = type === 'image' ? 
        `Results from ${getEngineName(data.engine)}` : 
        `Extracted from ${data.filename || 'PDF'}`;

    container.innerHTML = `
        <div class="bg-gray-50 rounded-xl p-6">
            <div class="flex items-center gap-3 mb-4">
                <svg class="w-6 h-6 success-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22,4 12,14.01 9,11.01"/>
                </svg>
                <h3 class="text-xl font-semibold text-gray-800">${title}</h3>
            </div>
            <div class="bg-white rounded-lg p-4 border-2 border-gray-200">
                <pre class="result-text text-gray-800">${data.text || 'No text found'}</pre>
            </div>
        </div>
    `;
}

// Show error
function showError(container, message) {
    container.innerHTML = `
        <div class="bg-red-50 border-2 border-red-200 rounded-xl p-6">
            <div class="flex items-center gap-3 mb-4">
                <svg class="w-6 h-6 error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
                <h3 class="text-xl font-semibold text-red-800">Error</h3>
            </div>
            <p class="text-red-700 mb-2">${message}</p>
            <p class="text-red-700">Please try again with a different file or settings.</p>
        </div>
    `;
}

// Get engine display name
function getEngineName(engineValue) {
    const engines = {
        'tesseract': 'Tesseract OCR',
        // 'easyocr': 'EasyOCR',
        'paddleocr': 'PaddleOCR',
        // 'compare': 'All Engines'
    };
    return engines[engineValue] || engineValue;
}

// Utility function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// File validation
function validateFile(file, type) {
    const maxSize = type === 'image' ? 10 * 1024 * 1024 : 50 * 1024 * 1024; // 10MB for images, 50MB for PDFs
    
    if (file.size > maxSize) {
        throw new Error(`File size too large. Maximum size is ${formatFileSize(maxSize)}.`);
    }
    
    if (type === 'image' && !file.type.startsWith('image/')) {
        throw new Error('Please select a valid image file.');
    }
    
    if (type === 'pdf' && file.type !== 'application/pdf') {
        throw new Error('Please select a valid PDF file.');
    }
    
    return true;
}

// Add visual feedback for processing state
function setProcessingState(processing) {
    isProcessing = processing;
    const uploadAreas = document.querySelectorAll('.upload-area');
    
    uploadAreas.forEach(area => {
        if (processing) {
            area.style.opacity = '0.6';
            area.style.pointerEvents = 'none';
        } else {
            area.style.opacity = '1';
            area.style.pointerEvents = 'auto';
        }
    });
}