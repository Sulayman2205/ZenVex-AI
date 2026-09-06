/* ==========================================
   ZENVEX - MAIN JAVASCRIPT
========================================== */

document.addEventListener("DOMContentLoaded", function () {


    /* ==========================================
       FILE UPLOAD DISPLAY
    ========================================== */

    /* PDF Q&A */

    const pdfInput = document.getElementById("pdf");
    const pdfDropzone = document.getElementById("pdf-dropzone");
    const pdfFileName = document.getElementById("pdf-file-name");
    const pdfFileInfo = document.getElementById("pdf-file-info");
    const pdfUploadIcon = document.getElementById("pdf-upload-icon");

    if (pdfInput) {

        pdfInput.addEventListener("change", function () {

            if (this.files && this.files.length > 0) {

                const file = this.files[0];

                if (pdfFileName) {
                    pdfFileName.textContent = file.name;
                }

                if (pdfFileInfo) {
                    pdfFileInfo.textContent = "PDF document selected";
                }

                if (pdfUploadIcon) {
                    pdfUploadIcon.textContent = "📄";
                }

                if (pdfDropzone) {
                    pdfDropzone.classList.add("file-selected");
                }

            }

        });

    }


    /* RESUME ANALYZER */

    const resumeInput = document.getElementById("resume");
    const resumeDropzone = document.getElementById("resume-dropzone");
    const resumeFileName = document.getElementById("resume-file-name");
    const resumeFileInfo = document.getElementById("resume-file-info");
    const resumeUploadIcon = document.getElementById("resume-upload-icon");

    if (resumeInput) {

        resumeInput.addEventListener("change", function () {

            if (this.files && this.files.length > 0) {

                const file = this.files[0];

                if (resumeFileName) {
                    resumeFileName.textContent = file.name;
                }

                if (resumeFileInfo) {
                    resumeFileInfo.textContent = "PDF resume selected";
                }

                if (resumeUploadIcon) {
                    resumeUploadIcon.textContent = "📄";
                }

                if (resumeDropzone) {
                    resumeDropzone.classList.add("file-selected");
                }

            }

        });

    }


    /* ==========================================
       LOADING STATES
    ========================================== */


    /*
       PHISHING URL DETECTOR
    */

    const phishingForm = document.querySelector(
        'form[action*="phishing"], .detector-card form'
    );

    if (phishingForm) {

        phishingForm.addEventListener("submit", function () {

            const button = this.querySelector("button");

            if (!button) {
                return;
            }

            button.disabled = true;

            button.innerHTML = `
                <span class="loading-spinner"></span>
                Analyzing URL...
            `;

            this.classList.add("form-loading");

        });

    }


    /*
       SPAM & FRAUD DETECTOR
    */

    const spamForm = document.querySelector(
        'form[action*="spam"], .spam-form'
    );

    if (spamForm) {

        spamForm.addEventListener("submit", function () {

            const button = this.querySelector("button");

            if (!button) {
                return;
            }

            button.disabled = true;

            button.innerHTML = `
                <span class="loading-spinner"></span>
                Analyzing Message...
            `;

            this.classList.add("form-loading");

        });

    }


    /*
       RESUME ANALYZER
    */

    const resumeForm = document.querySelector(
        'form[enctype="multipart/form-data"]'
    );

    /*
       Only attach this if the resume input exists.
       This prevents the PDF Q&A form from being
       accidentally treated as a resume form.
    */

    if (resumeForm && resumeInput) {

        resumeForm.addEventListener("submit", function () {

            const button = this.querySelector("button");

            if (!button) {
                return;
            }

            button.disabled = true;

            button.innerHTML = `
                <span class="loading-spinner"></span>
                Analyzing Resume...
            `;

            this.classList.add("form-loading");

        });

    }


    /*
       PDF Q&A
    */

    const pdfForm = document.querySelector(
        'form[enctype="multipart/form-data"]'
    );

    /*
       Only attach this if the PDF input exists.
    */

    if (pdfForm && pdfInput) {

        pdfForm.addEventListener("submit", function () {

            const button = this.querySelector("button");

            if (!button) {
                return;
            }

            button.disabled = true;

            button.innerHTML = `
                <span class="loading-spinner"></span>
                Analyzing Document...
            `;

            this.classList.add("form-loading");

        });

    }


});