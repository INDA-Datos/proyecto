document.addEventListener("DOMContentLoaded", function () {
    const uploadForm = document.getElementById("upload-form");

    if (uploadForm) {
        uploadForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const modal = document.getElementById("modal");
            if (modal) modal.style.display = "flex";

            const formData = new FormData();
            const fileInput = document.getElementById("file-input");

            if (!fileInput || fileInput.files.length === 0) {
                if (modal) modal.style.display = "none";
                alert("Por favor, selecciona un archivo.");
                return;
            }

            formData.append("file", fileInput.files[0]);

            try {
                const response = await fetch("/process_models", {
                    method: "POST",
                    body: formData,
                });

                const data = await response.json();
                if (modal) modal.style.display = "none";

                if (data.error) {
                    alert(`Error: ${data.error}`);
                    return;
                }

                const resultsSection = document.getElementById("results-section");
                const resultsContainer = document.getElementById("results-container");

                if (resultsSection && resultsContainer) {
                    resultsSection.classList.remove("hidden");
                    resultsContainer.innerHTML = `
                        <h3>Resultados de Clasificación</h3>
                        <p><strong>Accuracy:</strong> ${data.classification.accuracy.toFixed(2)}</p>
                        <pre>${JSON.stringify(data.classification.report, null, 2)}</pre>
                        <h3>Resultados de Regresión</h3>
                        <p><strong>MSE:</strong> ${data.regression.mse.toFixed(2)}</p>
                        <p><strong>R2 Score:</strong> ${data.regression.r2.toFixed(2)}</p>
                    `;
                }
            } catch (error) {
                if (modal) modal.style.display = "none";
                alert(`Error procesando datos: ${error}`);
            }
        });
    }
});