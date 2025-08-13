        lucide.createIcons();
        
        // DOM Elements
        const fileInput = document.getElementById('fileInput');
        const dropZone = document.getElementById('dropZone');
        const filePreview = document.getElementById('filePreview');
        const previewContent = document.getElementById('previewContent');
        const removeFile = document.getElementById('removeFile');
        const extractBtn = document.getElementById('extractBtn');
        const clearBtn = document.getElementById('clearBtn');
        const copyBtn = document.getElementById('copyBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const resultText = document.getElementById('resultText');
        const loadingOverlay = document.getElementById('loadingOverlay');
        const successMessage = document.getElementById('successMessage');
        const errorMessage = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        const languageSelect = document.getElementById('languageSelect');

        // File Handling
        fileInput.addEventListener('change', handleFileSelect);
        removeFile.addEventListener('click', clearFile);

        // Drag and Drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        dropZone.addEventListener('drop', handleDrop, false);

        // Buttons
        extractBtn.addEventListener('click', extractText);
        clearBtn.addEventListener('click', clearAll);
        copyBtn.addEventListener('click', copyText);
        downloadBtn.addEventListener('click', downloadText);

        // Functions
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        function highlight() {
            dropZone.classList.add('border-slate-400', 'bg-white/5');
        }

        function unhighlight() {
            dropZone.classList.remove('border-slate-400', 'bg-white/5');
        }

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length) {
                fileInput.files = files;
                handleFileSelect();
            }
        }

        function handleFileSelect() {
            const file = fileInput.files[0];
            if (!file) return;

            // Enable extract button
            extractBtn.disabled = false;
            clearBtn.disabled = false;

            // Show preview
            showFilePreview(file);
        }

        function showFilePreview(file) {
            filePreview.classList.remove('hidden');
            previewContent.innerHTML = '';

            if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.classList.add('max-h-48', 'rounded-lg', 'object-contain');
                previewContent.innerHTML = `
                    <div class="w-16 h-16 bg-slate-700 rounded-lg flex items-center justify-center">
                        <i data-lucide="image" class="w-8 h-8 text-slate-300"></i>
                    </div>
                    <div>
                        <p class="text-white font-medium">${file.name}</p>
                        <p class="text-slate-400 text-sm">${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                `;
                previewContent.querySelector('div').prepend(img);
            } else if (file.type === 'application/pdf') {
                previewContent.innerHTML = `
                    <div class="w-16 h-16 bg-slate-700 rounded-lg flex items-center justify-center">
                        <i data-lucide="file-text" class="w-8 h-8 text-slate-300"></i>
                    </div>
                    <div>
                        <p class="text-white font-medium">${file.name}</p>
                        <p class="text-slate-400 text-sm">${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                `;
            } else {
                previewContent.innerHTML = `
                    <div class="w-16 h-16 bg-slate-700 rounded-lg flex items-center justify-center">
                        <i data-lucide="file" class="w-8 h-8 text-slate-300"></i>
                    </div>
                    <div>
                        <p class="text-white font-medium">${file.name}</p>
                        <p class="text-slate-400 text-sm">Unsupported preview</p>
                    </div>
                `;
            }
            
            // Refresh icons
            lucide.createIcons();
        }

        function clearFile() {
            fileInput.value = '';
            filePreview.classList.add('hidden');
            extractBtn.disabled = true;
        }

        function clearAll() {
            clearFile();
            resultText.value = '';
            successMessage.classList.add('hidden');
            errorMessage.classList.add('hidden');
            copyBtn.disabled = true;
            downloadBtn.disabled = true;
        }

        async function extractText() {
            const file = fileInput.files[0];
            if (!file) return;

            // Reset UI
            resultText.value = '';
            successMessage.classList.add('hidden');
            errorMessage.classList.add('hidden');
            loadingOverlay.classList.remove('hidden');
            extractBtn.disabled = true;

            try {
                const formData = new FormData();
                formData.append('file', file);
                const language = languageSelect.value || 'en';

                const response = await fetch(`/api/extract?lang=${encodeURIComponent(language)}`, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(await response.text());
                }

                const data = await response.json();
                resultText.value = data.text;
                successMessage.classList.remove('hidden');
                copyBtn.disabled = false;
                downloadBtn.disabled = false;
            } catch (error) {
                console.error('Extraction error:', error);
                errorText.textContent = error.message || 'An error occurred during processing';
                errorMessage.classList.remove('hidden');
            } finally {
                loadingOverlay.classList.add('hidden');
                extractBtn.disabled = false;
                lucide.createIcons();
            }
        }

        function copyText() {
            if (!resultText.value) return;

            navigator.clipboard.writeText(resultText.value)
                .then(() => {
                    const originalHTML = copyBtn.innerHTML;
                    copyBtn.innerHTML = '<i data-lucide="check" class="w-5 h-5"></i>';
                    copyBtn.classList.add('bg-green-500', 'hover:bg-green-600');
                    
                    setTimeout(() => {
                        copyBtn.innerHTML = originalHTML;
                        copyBtn.classList.remove('bg-green-500', 'hover:bg-green-600');
                        lucide.createIcons();
                    }, 2000);
                })
                .catch(err => {
                    console.error('Copy failed:', err);
                });
        }

        function downloadText() {
            if (!resultText.value) return;

            const blob = new Blob([resultText.value], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `textlens-extraction-${new Date().toISOString().slice(0,10)}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
