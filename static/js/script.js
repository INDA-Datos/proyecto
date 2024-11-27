document.addEventListener("DOMContentLoaded", function () {
    const menuBtn = document.getElementById("menu-btn");
    const sidebarContent = document.getElementById("sidebar-content");

    // Función para mostrar y ocultar el menú lateral
    function toggleSidebar() {
        if (sidebarContent) {
            sidebarContent.classList.toggle("show");
        }
    }

    // Evento para abrir y cerrar el sidebar
    menuBtn.addEventListener("click", () => {
        sidebarContent.classList.toggle("show");
    });


    // Asegurar que el evento click esté conectado al botón
    if (menuBtn) {
        menuBtn.addEventListener("click", toggleSidebar);
    }

    // Evento del formulario para procesar archivos
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
                const response = await fetch("/process_data", {
                    method: "POST",
                    body: formData,
                });

                const data = await response.json();
                if (modal) modal.style.display = "none";

                if (data.error) {
                    alert(`Error: ${data.error}`);
                    return;
                }

                // Mostrar resultados en la sección de KPIs
                const kpiContainer = document.getElementById("kpi-container");
                if (kpiContainer) {
                    kpiContainer.innerHTML = ""; // Limpiar contenido anterior
                    Object.entries(data.kpis).forEach(([key, value]) => {
                        const kpiCard = document.createElement("div");
                        kpiCard.className = "kpi-card";
                        kpiCard.innerHTML = `<h3>${key}</h3><p>${value}</p>`;
                        kpiContainer.appendChild(kpiCard);
                    });
                }

                // Mostrar valores atípicos
                const outlierContainer = document.getElementById("outlier-container");
                if (outlierContainer) {
                    outlierContainer.innerHTML = ""; // Limpiar contenido anterior
                    Object.entries(data.outliers).forEach(([key, value]) => {
                        const outlierCard = document.createElement("div");
                        outlierCard.className = "outlier-card";
                        outlierCard.innerHTML = `<h3>${key}</h3><p>${value}</p>`;
                        outlierContainer.appendChild(outlierCard);
                    });
                }

                // Mostrar gráficos
                const graphContainer = document.getElementById("graph-container");
                if (graphContainer) {
                    graphContainer.innerHTML = ""; // Limpiar contenido anterior
                    data.graphs.forEach((graphUrl) => {
                        const graphCard = document.createElement("div");
                        graphCard.className = "graph-card";
                        const img = document.createElement("img");
                        img.src = graphUrl;
                        img.alt = "Gráfico generado";
                        graphCard.appendChild(img);
                        graphContainer.appendChild(graphCard);
                    });
                }
            } catch (error) {
                if (modal) modal.style.display = "none";
                alert(`Error procesando datos: ${error}`);
            }
        });
    }
});
