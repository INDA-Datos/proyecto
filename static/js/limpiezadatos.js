document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("upload-form");
    const modal = document.getElementById("modal");
    const resultsSection = document.getElementById("results-section");
    const cleaningResults = document.getElementById("cleaning-results");
    const fileInput = document.getElementById("file-input");

    // Validar la existencia de los elementos esenciales
    if (!uploadForm || !modal || !resultsSection || !cleaningResults || !fileInput) {
        console.error("Algunos elementos requeridos no están presentes en el DOM.");
        return;
    }

    // Evento para manejar el formulario de subida
    uploadForm.addEventListener("submit", async (event) => {
        event.preventDefault(); // Prevenir el envío por defecto del formulario

        // Mostrar el modal de carga
        modal.style.display = "flex";

        // Validar si se seleccionó un archivo
        if (fileInput.files.length === 0) {
            modal.style.display = "none";
            alert("Por favor, selecciona un archivo.");
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        try {
            // Llamada al backend para limpiar los datos
            const response = await fetch("/process_cleaning", {
                method: "POST",
                body: formData,
            });

            // Verificar si la respuesta es válida
            if (!response.ok) {
                throw new Error(`Error en la respuesta del servidor: ${response.statusText}`);
            }

            const data = await response.json();

            // Ocultar el modal después de procesar
            modal.style.display = "none";

            // Manejar errores del backend
            if (data.error) {
                alert(`Error del servidor: ${data.error}`);
                return;
            }

            // Mostrar resultados de limpieza en el frontend
            resultsSection.classList.remove("hidden");
            cleaningResults.innerHTML = `
                <div>
                    <h3>Valores fuera de rango en 'age':</h3>
                    <p>${data.outliers || 0} registros eliminados</p>
                </div>
                <div>
                    <h3>Columnas eliminadas:</h3>
                    <p>${data.columns_removed.length > 0 ? data.columns_removed.join(", ") : "Ninguna columna eliminada"}</p>
                </div>
                <div>
                    <h3>Archivo limpio generado:</h3>
                    <a href="${data.cleaned_file}" download>Descargar archivo limpio</a>
                </div>
            `;
        } catch (error) {
            // Ocultar el modal en caso de error
            modal.style.display = "none";
            console.error("Error durante la limpieza:", error);
            alert(`Error procesando datos: ${error.message}`);
        }
    });
});
